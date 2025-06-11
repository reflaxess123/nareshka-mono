import Adminka from '@/pages/Adminka/ui/Adminka';
import { lazy } from 'react';
import type { AppRoute } from './types';

const Home = lazy(() =>
  import('@/pages/Adminka').then((module) => ({ default: module.Adminka }))
);
const Profile = lazy(() =>
  import('@/pages/Profile').then((module) => ({ default: module.Profile }))
);
const Tasks = lazy(() =>
  import('@/pages/Tasks').then((module) => ({ default: module.Tasks }))
);
const Theory = lazy(() =>
  import('@/pages/Theory').then((module) => ({ default: module.Theory }))
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

export enum AppRoutes {
  HOME = '/',
  TASKS = '/tasks',
  THEORY = '/theory',
  PROFILE = '/profile',
  ADMIN_PANEL = '/admin-panel',
  ADMIN_USERS = '/admin/users',
  ADMIN_STATS = '/admin/stats',
}

export const routeConfig: AppRoute[] = [
  { path: AppRoutes.HOME, element: <Home /> },
  { path: AppRoutes.TASKS, element: <Tasks /> },
  { path: AppRoutes.THEORY, element: <Theory /> },
  { path: AppRoutes.PROFILE, element: <Profile /> },
  { path: AppRoutes.ADMIN_PANEL, element: <Adminka /> },
  { path: AppRoutes.ADMIN_USERS, element: <UserManagement /> },
  { path: AppRoutes.ADMIN_STATS, element: <DetailedStats /> },
];
