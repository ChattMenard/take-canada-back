import { describe, expect, it } from "vitest";
import { formatBytes, formatDate, shortHash } from "./format.js";

describe("formatBytes", () => {
  it("formats empty and byte values", () => {
    expect(formatBytes(null)).toBe("0 B");
    expect(formatBytes(0)).toBe("0 B");
    expect(formatBytes(512)).toBe("512 B");
  });

  it("formats larger byte counts with one decimal place", () => {
    expect(formatBytes(1536)).toBe("1.5 KB");
    expect(formatBytes(1024 * 1024 * 2.25)).toBe("2.3 MB");
  });
});

describe("formatDate", () => {
  it("handles missing and invalid values", () => {
    expect(formatDate(null)).toBe("—");
    expect(formatDate("not-a-date")).toBe("not-a-date");
  });

  it("formats valid dates into readable strings", () => {
    expect(formatDate("2025-01-02T03:04:05.000Z")).toContain("2025");
  });
});

describe("shortHash", () => {
  it("returns an empty string for missing hashes", () => {
    expect(shortHash(null)).toBe("");
  });

  it("keeps the front and back of a hash", () => {
    expect(shortHash("abcdef0123456789fedcba9876543210")).toBe("abcdef0123…543210");
  });
});
