import { create } from "zustand";

const ALL_TRACKS = ["funding", "patent", "simulation", "agreement", "general"];

export const useVisualizationStore = create((set) => ({
  timelineRange: [2005, 2023],
  timelineTracks: ALL_TRACKS,
  networkLayers: ["DARPA", "Gates", "NIH", "Private"],
  selectedEvidence: null,
  setTimelineRange: (timelineRange) => set({ timelineRange }),
  toggleTimelineTrack: (track) =>
    set((state) => ({
      timelineTracks: state.timelineTracks.includes(track)
        ? state.timelineTracks.filter((item) => item !== track)
        : [...state.timelineTracks, track],
    })),
  toggleNetworkLayer: (layer) =>
    set((state) => ({
      networkLayers: state.networkLayers.includes(layer)
        ? state.networkLayers.filter((item) => item !== layer)
        : [...state.networkLayers, layer],
    })),
  setSelectedEvidence: (selectedEvidence) => set({ selectedEvidence }),
}));
