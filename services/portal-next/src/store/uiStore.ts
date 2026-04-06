import { create } from 'zustand';

export type ViewType = 'conversation' | 'knowledge';

export type ItemType = 'collection' | 'file' | 'chunk';

export interface ActiveItem {
  type: ItemType;
  id: string;
  data: any;
}

export interface UIStore {
  activeView: ViewType;
  setActiveView: (view: ViewType) => void;
  
  activeItem: ActiveItem | null;
  setActiveItem: (item: ActiveItem | null) => void;
  
  isInspectorOpen: boolean;
  setIsInspectorOpen: (open: boolean) => void;
  toggleInspector: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  activeView: 'conversation',
  setActiveView: (view) => set({ activeView: view }),
  
  activeItem: null,
  setActiveItem: (item) => set({ activeItem: item }),
  
  isInspectorOpen: false,
  setIsInspectorOpen: (open) => set({ isInspectorOpen: open }),
  toggleInspector: () => set((state) => ({ isInspectorOpen: !state.isInspectorOpen })),
}));
