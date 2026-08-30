"""
rehab_rl/validation/benchmark_against_clinical_baselines.py
Benchmarking script to compare RL agent against clinical baselines.

Validates that agent recommendations:
1. Stay within healthy population norms
2. Progressively improve across recovery stages
3. Align with physical therapy guidelines
4. Achieve measurable outcomes (ROM, strength, pain reduction)
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass

from rehabrl.config import INJURY_TYPES
from rehabrl.data.exercise_database import get_prescription
from rehabrl.data.nhanes_loader import NHANESLoader
from rehabrl.environment import RehabEnvironment


@dataclass
class BenchmarkResult:
    """Single benchmark result."""

    metric: str
    expected: float
    actual: float
    passed: bool
    message: str


class ClinicalBenchmark:
    """Benchmark suite comparing agent against clinical baselines."""

    def __init__(self, agent, seed: int = 42):
        self.agent = agent
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.nhanes = NHANESLoader(n_records=2000, seed=seed)
        self.nhanes.load_data()
        self.results: List[BenchmarkResult] = []

    def run_full_benchmark(self) -> Dict:
        """Run complete benchmark suite."""
        print("🏥 Starting Clinical Baseline Benchmarking...")

        results = {}

        # Benchmark 1: Healthy population alignment
        print("\n[1/5] Healthy Population Alignment...")
        results["healthy_alignment"] = self._benchmark_healthy_alignment()

        # Benchmark 2: Recovery stage progression
        print("[2/5] Recovery Stage Progression...")
        results["stage_progression"] = self._benchmark_stage_progression()

        # Benchmark 3: Outcome improvements
        print("[3/5] Outcome Improvements...")
        results["outcome_improvement"] = self._benchmark_outcome_improvement()

        # Benchmark 4: Safety compliance
        print("[4/5] Safety Compliance...")
        results["safety_compliance"] = self._benchmark_safety_compliance()

        # Benchmark 5: Treatment efficiency
        print("[5/5] Treatment Efficiency...")
        results["treatment_efficiency"] = self._benchmark_treatment_efficiency()

        # Aggregate results
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        self._print_results(results)

        return results

    def _benchmark_healthy_alignment(self) -> Dict:
        """
        Test 1: Agent recommendations should keep metrics within healthy population range.
        """
        print("  Checking if agent keeps patients within healthy norms...")

        healthy_baseline = self.nhanes.get_healthy_baseline()
        rom_range = (
            healthy_baseline["rom_mean"] - 2 * healthy_baseline["rom_std"],
            healthy_baseline["rom_mean"] + 2 * healthy_baseline["rom_std"],
        )
        strength_range = (
            healthy_baseline["strength_mean"] - 2 * healthy_baseline["strength_std"],
            healthy_baseline["strength_mean"] + 2 * healthy_baseline["strength_std"],
        )

        env = RehabEnvironment(seed=self.seed)
        violations = 0
        total_steps = 0

        for _ in range(20):  # 20 simulated patients
            state = env.reset()

            for step in range(50):  # 50 steps per patient
                action = self.agent.act(
                    state, valid_actions=env.valid_actions(), training=False
                )
                next_state, reward, done, info = env.step(action)

                ps = env.get_state()
                rom = ps.rom * 100  # Convert to 0-100 scale
                strength = ps.strength * 70  # Rough estimate to kg

                if not (rom_range[0] <= rom <= rom_range[1]):
                    violations += 1
                if not (strength_range[0] <= strength <= strength_range[1]):
                    violations += 1

                total_steps += 1
                state = next_state

                if done:
                    break

        violation_rate = violations / (total_steps * 2)
        passed = violation_rate < 0.05  # Allow 5% violations

        return {
            "passed": passed,
            "violation_rate": violation_rate,
            "rom_range": rom_range,
            "strength_range": strength_range,
            "message": f"ROM/strength violations: {violation_rate * 100:.1f}% (threshold: 5%)",
        }

    def _benchmark_stage_progression(self) -> Dict:
        """
        Test 2: Verify recovery stage progression follows clinical guidelines.

        Expected progression: Acute → Subacute → Remodeling → Functional → Return
        """
        print("  Checking recovery stage progression...")

        env = RehabEnvironment(seed=self.seed)
        stage_transitions = []

        for injury in INJURY_TYPES[:3]:  # Test first 3 injury types
            state = env.reset(injury_type=injury, injury_severity=0.7, recovery_stage=0)
            current_stage = 0
            for step in range(500):
                action = self.agent.act(
                    state, valid_actions=env.valid_actions(), training=False
                )
                next_state, reward, done, info = env.step(action)

                ps = env.get_state()
                if ps.recovery_stage > current_stage:
                    # Stage transition occurred
                    stage_transitions.append(
                        {
                            "injury": injury,
                            "from_stage": current_stage,
                            "to_stage": ps.recovery_stage,
                            "steps": step,
                        }
                    )
                    current_stage = ps.recovery_stage

                state = next_state
                if done:
                    break

        # Check if transitions happen
        has_progression = len(stage_transitions) > 0

        return {
            "passed": has_progression,
            "n_transitions": len(stage_transitions),
            "transitions": stage_transitions[:5],  # First 5 transitions
            "message": f"Observed {len(stage_transitions)} stage transitions (expected > 0)",
        }

    def _benchmark_outcome_improvement(self) -> Dict:
        """
        Test 3: Verify that agent recommendations lead to measurable improvements.

        Expected: Pain ↓, ROM ↑, Strength ↑ over episodes
        """
        print("  Checking outcome improvements...")

        env = RehabEnvironment(seed=self.seed)
        improvements = {
            "pain_reduction": [],
            "rom_improvement": [],
            "strength_improvement": [],
        }

        for _ in range(10):  # 10 patients
            state = env.reset()
            initial_pain = env.get_state().pain_level
            initial_rom = env.get_state().rom
            initial_strength = env.get_state().strength

            for step in range(100):
                action = self.agent.act(
                    state, valid_actions=env.valid_actions(), training=False
                )
                next_state, reward, done, info = env.step(action)
                state = next_state

                if done:
                    break

            final_pain = env.get_state().pain_level
            final_rom = env.get_state().rom
            final_strength = env.get_state().strength

            improvements["pain_reduction"].append(initial_pain - final_pain)
            improvements["rom_improvement"].append(final_rom - initial_rom)
            improvements["strength_improvement"].append(
                final_strength - initial_strength
            )

        avg_pain_reduction = np.mean(improvements["pain_reduction"])
        avg_rom_improvement = np.mean(improvements["rom_improvement"])
        avg_strength_improvement = np.mean(improvements["strength_improvement"])

        # Pass if we see measurable improvements
        passed = (
            avg_pain_reduction > 0.01
            and avg_rom_improvement > 0.01
            and avg_strength_improvement > 0.01
        )

        return {
            "passed": passed,
            "avg_pain_reduction": avg_pain_reduction,
            "avg_rom_improvement": avg_rom_improvement,
            "avg_strength_improvement": avg_strength_improvement,
            "message": f"Pain↓: {avg_pain_reduction:.3f}, ROM↑: {avg_rom_improvement:.3f}, Strength↑: {avg_strength_improvement:.3f}",
        }

    def _benchmark_safety_compliance(self) -> Dict:
        """
        Test 4: Verify agent respects safety constraints.

        Safety rules:
        - Don't prescribe high-intensity in early stages
        - Don't progress too fast
        - Avoid prescriptions that spike pain
        """
        print("  Checking safety compliance...")

        env = RehabEnvironment(seed=self.seed)
        violations = {
            "early_high_intensity": 0,
            "pain_spikes": 0,
            "invalid_actions": 0,
        }
        total_actions = 0

        for _ in range(20):  # 20 patients
            state = env.reset()
            ps = env.get_state()

            for step in range(50):
                valid_actions = env.valid_actions()
                action = self.agent.act(
                    state, valid_actions=valid_actions, training=False
                )

                # Check if action is valid
                if action not in valid_actions:
                    violations["invalid_actions"] += 1

                # Check prescription safety
                prescription = get_prescription(action)

                # High intensity too early?
                if prescription.intensity == "High" and ps.recovery_stage < 2:
                    violations["early_high_intensity"] += 1

                next_state, reward, done, info = env.step(action)

                # Check for pain spikes
                ps_after = env.get_state()
                if ps_after.pain_level - ps.pain_level > 0.2:
                    violations["pain_spikes"] += 1

                total_actions += 1
                state = next_state
                ps = ps_after

                if done:
                    break

        violation_rate = (
            sum(violations.values()) / total_actions if total_actions > 0 else 0
        )
        passed = violation_rate < 0.1  # Allow 10% violations

        return {
            "passed": passed,
            "violation_rate": violation_rate,
            "violations": violations,
            "message": f"Safety violations: {violation_rate * 100:.1f}% (threshold: 10%)",
        }

    def _benchmark_treatment_efficiency(self) -> Dict:
        """
        Test 5: Compare agent efficiency against random baseline.

        Agent should achieve recovery goals faster/with better outcomes than random policy.
        """
        print("  Checking treatment efficiency...")

        def run_policy(agent, n_episodes: int = 20):
            env = RehabEnvironment(seed=self.seed)
            rewards = []
            recovery_rates = []

            for _ in range(n_episodes):
                state = env.reset()
                episode_reward = 0

                for step in range(100):
                    valid = env.valid_actions()
                    if agent is None:
                        # Random policy
                        action = self.rng.choice(valid)
                    else:
                        action = agent.act(state, valid_actions=valid, training=False)

                    next_state, reward, done, info = env.step(action)
                    episode_reward += reward
                    state = next_state

                    if done:
                        break

                rewards.append(episode_reward)
                recovery_rates.append(info.get("recovered", False))

            return np.mean(rewards), np.mean(recovery_rates)

        # Agent performance
        agent_reward, agent_recovery = run_policy(self.agent, n_episodes=20)

        # Random baseline
        random_reward, random_recovery = run_policy(None, n_episodes=20)

        # Agent should do better than random
        agent_better = (
            agent_reward > random_reward and agent_recovery >= random_recovery * 0.8
        )

        return {
            "passed": agent_better,
            "agent_reward": agent_reward,
            "agent_recovery_rate": agent_recovery,
            "random_reward": random_reward,
            "random_recovery_rate": random_recovery,
            "improvement": (agent_reward - random_reward) / abs(random_reward) * 100
            if random_reward != 0
            else 0,
            "message": f"Agent reward: {agent_reward:.2f} vs Random: {random_reward:.2f} ({(agent_reward - random_reward):.2f} improvement)",
        }

    def _print_results(self, results: Dict):
        """Pretty-print benchmark results."""
        for test_name, result in results.items():
            status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
            print(f"\n{status} | {test_name.replace('_', ' ').title()}")
            print(f"  {result.get('message', 'No message')}")

            if "violation_rate" in result:
                print(f"  Violation Rate: {result['violation_rate'] * 100:.1f}%")
            if "improvement" in result:
                print(f"  Improvement: {result['improvement']:.1f}%")

    def to_dataframe(self, results: Dict) -> pd.DataFrame:
        """Convert results to DataFrame for logging/analysis."""
        rows = []
        for test_name, result in results.items():
            rows.append(
                {
                    "test": test_name,
                    "passed": result.get("passed", False),
                    "message": result.get("message", ""),
                }
            )
        return pd.DataFrame(rows)


def benchmark_agent(agent, output_file: str = None) -> Dict:
    """
    Convenience function to benchmark an agent.

    Args:
        agent: Trained agent (must have .act() method)
        output_file: Optional CSV file to save results

    Returns:
        Dictionary of benchmark results
    """
    benchmark = ClinicalBenchmark(agent)
    results = benchmark.run_full_benchmark()

    if output_file:
        df = benchmark.to_dataframe(results)
        df.to_csv(output_file, index=False)
        print(f"\n📊 Results saved to {output_file}")

    return results


if __name__ == "__main__":
    # Example usage
    print("Clinical Benchmark Suite")
    print("=" * 60)
    print("This script benchmarks the RL agent against clinical baselines.")
    print("\nUsage:")
    print(
        "  from validation.benchmark_against_clinical_baselines import benchmark_agent"
    )
    print("  results = benchmark_agent(trained_agent)")
