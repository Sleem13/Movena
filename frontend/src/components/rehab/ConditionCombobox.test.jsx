import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";

import ConditionCombobox from "./ConditionCombobox.jsx";

const conditions = [
  { id: "acl_tear", name: "Anterior cruciate ligament injury", aliases: ["ACL tear"], category: "Knee", body_region: "Lower limb", rl_supported: true },
  { id: "stroke_rehabilitation", name: "Stroke rehabilitation", aliases: ["CVA", "post-stroke"], category: "Neurological", body_region: "Whole body", rl_supported: false },
];

it("searches condition aliases and selects the matching protocol", () => {
  const onChange = vi.fn();
  render(<ConditionCombobox conditions={conditions} label="Condition or diagnosis" value="acl_tear" onChange={onChange} />);

  const input = screen.getByRole("combobox", { name: "Condition or diagnosis" });
  fireEvent.change(input, { target: { value: "CVA" } });

  expect(screen.queryByRole("option", { name: /Anterior cruciate/ })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("option", { name: /Stroke rehabilitation/ }));
  expect(onChange).toHaveBeenCalledWith(conditions[1]);
});

it("supports keyboard selection from filtered results", () => {
  const onChange = vi.fn();
  render(<ConditionCombobox conditions={conditions} label="Condition or diagnosis" value="acl_tear" onChange={onChange} />);

  const input = screen.getByRole("combobox", { name: "Condition or diagnosis" });
  fireEvent.change(input, { target: { value: "post-stroke" } });
  fireEvent.keyDown(input, { key: "Enter" });

  expect(onChange).toHaveBeenCalledWith(conditions[1]);
});
