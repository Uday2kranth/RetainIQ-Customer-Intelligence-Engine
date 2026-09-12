#!/usr/bin/env python3
"""
RetainIQ: Automated Demo Scheduler & Trigger
Arm automated execution for a specific demo minute (e.g., 17:35, 17:40, 19:00).
- Updates dags/retainiq_pipeline_dag.py cron schedule to match
- Displays a real-time countdown in the terminal
- Automatically executes the end-to-end pipeline (with email alert + Power BI CSVs)
  at the exact scheduled second.
"""

import sys
import os
import time
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configure UTF-8 for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DAG_FILE = PROJECT_ROOT / "dags" / "retainiq_pipeline_dag.py"
LOG_FILE = PROJECT_ROOT / "data" / "automation_run.log"

def update_dag_cron(target_dt: datetime):
    """Updates the cron schedule expression inside dags/retainiq_pipeline_dag.py."""
    if not DAG_FILE.exists():
        return
    
    minute = target_dt.minute
    hour = target_dt.hour
    cron_expr = f"{minute} {hour} * * *"
    
    try:
        with open(DAG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace schedule line
        import re
        new_content = re.sub(
            r'schedule=[\'"][^\'"]*[\'"]',
            f'schedule="{cron_expr}"',
            content
        )
        with open(DAG_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[+] Synced Airflow DAG: schedule='{cron_expr}' (triggers daily at {hour:02d}:{minute:02d})")
    except Exception as e:
        print(f"[!] Warning updating DAG file: {e}")

def main():
    parser = argparse.ArgumentParser(description="RetainIQ Automated Demo Scheduler")
    parser.add_argument(
        "--time",
        type=str,
        default="17:35",
        help="Target trigger time in HH:MM (24-hour format, e.g., 17:35 or 19:00) or +Nm (e.g. +5m)"
    )
    parser.add_argument(
        "--mode",
        choices=["simulate", "standard", "reset"],
        default="simulate",
        help="Execution mode: simulate (+35 accounts for demo), standard (baseline), reset"
    )
    parser.add_argument(
        "--no-dag-update",
        action="store_true",
        help="Skip updating the DAG schedule expression"
    )
    args = parser.parse_args()

    now = datetime.now()

    # Parse target time
    if args.time.startswith("+") and args.time.endswith("m"):
        minutes_to_add = int(args.time[1:-1])
        target_time = now + timedelta(minutes=minutes_to_add)
    else:
        try:
            target_parts = args.time.split(":")
            target_hour = int(target_parts[0])
            target_minute = int(target_parts[1])
            target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            if target_time <= now:
                # If target is earlier today, ask or assume next day
                print(f"[!] Target time {args.time} has already passed today ({now.strftime('%H:%M:%S')}).")
                target_time += timedelta(days=1)
        except Exception as e:
            print(f"[x] Invalid time format: {args.time}. Use HH:MM (e.g., 17:35 or 19:00).")
            sys.exit(1)

    # Update DAG schedule
    if not args.no_dag_update:
        update_dag_cron(target_time)

    # Execution flag for run_pipeline.py
    runner_args = [sys.executable, str(PROJECT_ROOT / "run_pipeline.py")]
    if args.mode == "simulate":
        runner_args.append("--simulate")
    elif args.mode == "reset":
        runner_args.append("--reset")

    INFO_FILE = PROJECT_ROOT / "data" / "scheduler.info"
    try:
        import json
        with open(INFO_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "pid": os.getpid(),
                "target_time": target_time.strftime("%Y-%m-%d %H:%M:%S"),
                "target_time_display": target_time.strftime("%I:%M %p"),
                "mode": args.mode
            }, f)
    except Exception:
        pass

    print("\n" + "=" * 65)
    print(" RETAINIQ: AUTOMATED PIPELINE SCHEDULER")
    print("=" * 65)
    print(f" * System Clock        : {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" * Target Trigger Time : {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" * Execution Mode      : {args.mode.upper()} ({' '.join(runner_args[1:])})")
    print(f" * Airflow DAG Cron    : {target_time.minute} {target_time.hour} * * *")
    print(f" * Audit Log           : {LOG_FILE.name}")
    print("=" * 65)
    print(" [STATUS: ARMED] Monitoring clock in background...\n")

    try:
        # Countdown loop
        while True:
            current_now = datetime.now()
            remaining = target_time - current_now
            total_seconds = int(remaining.total_seconds())

            if total_seconds <= 0:
                break

            mins, secs = divmod(total_seconds, 60)
            hours, mins = divmod(mins, 60)
            sys.stdout.write(f"\r [{current_now.strftime('%H:%M:%S')}] T-minus {hours:02d}:{mins:02d}:{secs:02d} until automated trigger... ")
            sys.stdout.flush()
            
            sleep_duration = min(1.0, max(0.2, total_seconds))
            time.sleep(sleep_duration)

        print("\n\n" + "-" * 65)
        print(f" [TRIGGER] Scheduled target time reached: {datetime.now().strftime('%H:%M:%S')}. Executing pipeline...")
        print("-" * 65 + "\n")

        start_t = time.time()
        
        # Pass active recipients from data/recipients.json if present
        env = os.environ.copy()
        RECIPIENTS_FILE = PROJECT_ROOT / "data" / "recipients.json"
        if RECIPIENTS_FILE.exists():
            try:
                import json
                with open(RECIPIENTS_FILE, "r", encoding="utf-8") as rf:
                    recs = json.load(rf)
                if recs:
                    env["SALES_MANAGER_EMAIL"] = ", ".join(recs)
            except Exception:
                pass

        result = subprocess.run(runner_args, capture_output=False, env=env)
        elapsed = time.time() - start_t

        # Write audit log
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mode: {args.mode} | Exit Code: {result.returncode} | Runtime: {elapsed:.2f}s\n")

        # Write scheduler completion record
        COMPLETED_FILE = PROJECT_ROOT / "data" / "scheduler_completed.info"
        try:
            import json
            with open(COMPLETED_FILE, "w", encoding="utf-8") as cf:
                json.dump({
                    "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "completed_display": datetime.now().strftime("%I:%M %p"),
                    "mode": args.mode,
                    "exit_code": result.returncode,
                    "elapsed_seconds": round(elapsed, 2)
                }, cf)
        except Exception:
            pass

        print("\n" + "=" * 65)
        if result.returncode == 0:
            print(f" [SUCCESS] Automated Pipeline Trigger Completed in {elapsed:.2f}s")
            print(" Priority churn alert email sent via Gmail OAuth.")
            print(" Power BI analytical CSV views updated in data/processed/.")
        else:
            print(f" [ERROR] Pipeline exited with return code {result.returncode}.")
        print("=" * 65 + "\n")
    finally:
        if INFO_FILE.exists():
            try:
                INFO_FILE.unlink(missing_ok=True)
            except Exception:
                pass

if __name__ == "__main__":
    main()
