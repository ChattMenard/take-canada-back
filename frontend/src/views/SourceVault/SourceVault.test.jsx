import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import SourceVault from "./index.jsx";

vi.mock("../../api.js", () => ({
  api: {
    listEvidence: vi.fn(() => Promise.resolve([])),
    getEvidence: vi.fn(),
    downloadUrl: vi.fn(),
  },
}));

describe("SourceVault", () => {
  beforeEach(() => vi.clearAllMocks());

  it("filters the signed local index by source title", async () => {
    render(<SourceVault online={false} onPreserve={() => {}} />);
    await waitFor(() => expect(screen.getByText("8 sources")).toBeTruthy());

    fireEvent.change(screen.getByPlaceholderText(/Search titles/), {
      target: { value: "Lobbying Meetings" },
    });

    expect(screen.getByText("Lobbying Meetings Analysis")).toBeTruthy();
    expect(screen.queryByText("Political Donations Analysis")).toBeNull();
  });
});
