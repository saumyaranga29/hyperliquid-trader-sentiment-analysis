import subprocess
import sys

def main():
    print("==========================================================")
    print("         PRIMETRADE.AI QUANT RESEARCH PIPELINE           ")
    print("==========================================================")
    
    scripts = [
        ("data_pipeline.py", "1. Running Data Cleaning & Merging Pipeline..."),
        ("eda_analysis.py", "2. Running Exploratory Data Analysis & Statistics..."),
        ("trader_profiles.py", "3. Running Trader Profiling & Sentiment Behaviors..."),
        ("strategy_backtest.py", "4. Running Trading Strategy Backtesting..."),
        ("generate_report.py", "5. Compiling Markdown Reports..."),
        ("generate_pdf.py", "6. Compiling PDF Report...")
    ]
    
    for script_name, description in scripts:
        print(f"\n[+] {description}")
        result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"    Success: {script_name} completed.")
            # Print last few lines of stdout if any
            stdout_lines = result.stdout.strip().split("\n")
            if stdout_lines:
                print(f"    Summary: {stdout_lines[-1]}")
        else:
            print(f"    ERROR: {script_name} failed with return code {result.returncode}")
            print("    Stdout:")
            print(result.stdout)
            print("    Stderr:")
            print(result.stderr)
            sys.exit(1)
            
    print("\n==========================================================")
    print("Pipeline executed successfully! Reports generated.")
    print("- Workspace Markdown Report: report.md")
    print("- Workspace PDF Report: Primetrade_Quant_Research_Report.pdf")
    print("- Visualizations saved in: plots/")
    print("==========================================================")

if __name__ == "__main__":
    main()
