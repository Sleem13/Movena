import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EXERCISES } from "../../data/exercises.js";
import ExercisePoseGraph, { EXERCISE_POSE_GRAPHS } from "./ExercisePoseGraph.jsx";


describe("ExercisePoseGraph", () => {
  it("defines a distinct movement graph for every exercise in the library", () => {
    expect(Object.keys(EXERCISE_POSE_GRAPHS).sort()).toEqual(
      EXERCISES.map((exercise) => exercise.exercise_id).sort(),
    );
  });

  it("renders an accessible, exercise-addressable SVG", () => {
    render(<ExercisePoseGraph exerciseId="bodyweight_squat" label="Bodyweight Squat movement preview diagram" />);
    const graph = screen.getByRole("img", { name: "Bodyweight Squat movement preview diagram" });
    expect(graph).toHaveAttribute("data-exercise-pose", "bodyweight_squat");
  });
});
