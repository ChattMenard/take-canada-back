import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Navigation from "./Navigation.jsx";

describe("Navigation", () => {
  it("marks the current tier and navigates to the source vault", () => {
    const onNavigate = vi.fn();
    render(<Navigation activeView="dashboard" onNavigate={onNavigate} online />);

    expect(screen.getByRole("button", { name: "Overview" }).getAttribute("aria-current")).toBe("page");
    fireEvent.click(screen.getByRole("button", { name: "Source vault" }));
    expect(onNavigate).toHaveBeenCalledWith("vault");
  });

  it("reports local-index mode when the API is unavailable", () => {
    render(<Navigation activeView="dashboard" onNavigate={() => {}} online={false} />);
    expect(screen.getByText("Local index")).toBeTruthy();
  });
});
