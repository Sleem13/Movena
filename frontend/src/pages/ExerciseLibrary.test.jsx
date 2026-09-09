import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ExerciseLibrary from "./ExerciseLibrary.jsx";
import { EXERCISES } from "../data/exercises.js";

vi.mock("../context/AuthContext.jsx", () => ({ useAuth: () => ({ user: { role: "admin" } }) }));

describe("exercise discovery", () => {
  it("pages through every available exercise and resets pagination when filtering", () => {
    render(<ExerciseLibrary exercises={EXERCISES} onAnalyze={vi.fn()} />);
    const available = within(screen.getByRole("region", { name: "Available exercises" }));
    expect(available.getAllByRole("article")).toHaveLength(3);
    expect(screen.getByRole("button", { name: "Previous exercises" })).toBeDisabled();
    const seen = new Set();
    for (let page = 0; page < 4; page += 1) {
      available.getAllByRole("article").forEach((card) => seen.add(card.querySelector("h2").textContent));
      if (page < 3) fireEvent.click(screen.getByRole("button", { name: "Next exercises" }));
    }
    expect(seen.size).toBe(EXERCISES.filter((exercise) => exercise.supported_in_app).length);
    expect(screen.getByRole("button", { name: "Next exercises" })).toBeDisabled();
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "squat" } });
    expect(screen.getByRole("heading", { name: "Bodyweight Squat" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Clear exercise filters" }));
    expect(screen.getByRole("button", { name: "Previous exercises" })).toBeDisabled();
  });
  it("reveals planned results when searched without enabling unavailable analysis", () => {
    const onAnalyze = vi.fn();
    const { container } = render(<ExerciseLibrary exercises={EXERCISES} onAnalyze={onAnalyze} />);
    expect(container.querySelector("details")).not.toHaveAttribute("open");
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "lunge" } });
    expect(container.querySelector("details")).toHaveAttribute("open");
    expect(screen.getByRole("button", { name: "Not available" })).toBeDisabled();
    expect(onAnalyze).not.toHaveBeenCalled();
    expect(screen.getByRole("status")).toHaveTextContent("1 exercise");
  });

  it("recovers from an empty search and starts the chosen exercise", () => {
    const onAnalyze = vi.fn();
    render(<ExerciseLibrary exercises={EXERCISES} onAnalyze={onAnalyze} />);
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "no-such-exercise" } });
    expect(screen.queryAllByRole("article")).toHaveLength(0);
    fireEvent.click(screen.getByRole("button", { name: "Clear", exact: true }));
    expect(screen.getByRole("searchbox")).toHaveValue("");
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "squat" } });
    fireEvent.click(screen.getByRole("button", { name: "Analyze this exercise" }));
    expect(onAnalyze).toHaveBeenCalledWith("bodyweight_squat");
  });
});
