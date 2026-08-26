import { fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { describe, expect, it } from "vitest";

import Select from "./Select.jsx";

const OPTIONS = [
  { value: "one", label: "First option" },
  { value: "two", label: "Second option" },
];

function ControlledSelect() {
  const [value, setValue] = useState("one");
  return <Select ariaLabel="Example choice" value={value} onChange={setValue} options={OPTIONS} />;
}

describe("Select", () => {
  it("opens its branded menu and changes the selected value", () => {
    render(<ControlledSelect />);
    fireEvent.click(screen.getByRole("combobox", { name: "Example choice" }));
    fireEvent.click(screen.getByRole("option", { name: "Second option" }));
    expect(screen.getByRole("combobox", { name: "Example choice" })).toHaveTextContent("Second option");
  });

  it("supports keyboard selection", () => {
    render(<ControlledSelect />);
    const trigger = screen.getByRole("combobox", { name: "Example choice" });
    fireEvent.keyDown(trigger, { key: "ArrowDown" });
    fireEvent.keyDown(screen.getByRole("listbox", { name: "Example choice" }), { key: "Enter" });
    expect(trigger).toHaveTextContent("Second option");
  });
});
