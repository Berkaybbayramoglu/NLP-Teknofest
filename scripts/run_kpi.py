import argparse, os
from agentkit.agent.core import build_agent
from agentkit.kpi.evaluator import KPIEvaluator

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="scenarios/scenario1.json")
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--no-unsloth", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.cpu:
        os.environ["FORCE_CPU"] = "1"
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    agent = build_agent(use_unsloth=not args.no_unsloth)
    kpi = KPIEvaluator(agent)
    df = kpi.run(args.scenario, save_csv=args.out, verbose=args.verbose)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
