import { contentBlockSlice } from '@/entities/ContentBlock';
import theorySlice from '@/entities/TheoryCard/model/slice';
import sidebarSlice from '@/widgets/Sidebar/model/slice/sidebarSlice';

export const rootReducer = {
  sidebar: sidebarSlice,
  contentBlock: contentBlockSlice,
  theory: theorySlice,
};
