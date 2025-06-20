import Adminka from '@/pages/Adminka/ui/Adminka';
import Home from '@/pages/Home/ui/Home';
import { lazy } from 'react';
import type { AppRoute } from './types';

const GetStarted = lazy(() =>
  import('@/pages/GetStarted').then((module) => ({
    default: module.GetStarted,
  }))
);
const Profile = lazy(() =>
  import('@/pages/Profile').then((module) => ({ default: module.Profile }))
);
const Settings = lazy(() =>
  import('@/pages/Settings').then((module) => ({ default: module.Settings }))
);
const Tasks = lazy(() =>
  import('@/pages/Tasks').then((module) => ({ default: module.Tasks }))
);

const UserManagement = lazy(() =>
  import('@/pages/Admin/UserManagement').then((module) => ({
    default: module.UserManagement,
  }))
);
const DetailedStats = lazy(() =>
  import('@/pages/Admin/DetailedStats').then((module) => ({
    default: module.DetailedStats,
  }))
);
const CodeEditor = lazy(() =>
  import('@/pages/CodeEditor').then((module) => ({
    default: module.CodeEditorPage,
  }))
);
const MindMap = lazy(() =>
  import('@/pages/MindMap/ui/MindMapPage').then((module) => ({
    default: module.default,
  }))
);

export enum AppRoutes {
  HOME = '/',
  GET_STARTED = '/get-started',
  TASKS = '/tasks',
  PROFILE = '/profile',
  SETTINGS = '/settings',
  CODE_EDITOR = '/code-editor',
  MINDMAP = '/mindmap',
  ADMIN_PANEL = '/admin-panel',
  ADMIN_USERS = '/admin/users',
  ADMIN_STATS = '/admin/stats',
}

export const routeConfig: AppRoute[] = [
  { path: AppRoutes.HOME, element: <Home /> },
  { path: AppRoutes.GET_STARTED, element: <GetStarted /> },
  { path: AppRoutes.TASKS, element: <Tasks /> },

  { path: AppRoutes.PROFILE, element: <Profile /> },
  { path: AppRoutes.SETTINGS, element: <Settings /> },
  { path: AppRoutes.CODE_EDITOR, element: <CodeEditor /> },
  { path: AppRoutes.MINDMAP, element: <MindMap /> },
  { path: AppRoutes.ADMIN_PANEL, element: <Adminka /> },
  { path: AppRoutes.ADMIN_USERS, element: <UserManagement /> },
  { path: AppRoutes.ADMIN_STATS, element: <DetailedStats /> },
];
