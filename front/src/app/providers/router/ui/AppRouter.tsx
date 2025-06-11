import { routeConfig } from '@/app/providers/router/model/routeConfig';
import { Loading } from '@/shared/components/Loading';
import { PageTransition } from '@/shared/components/PageTransition';
import { Sidebar } from '@/widgets/Sidebar';
import { Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

export const AppRouter = () => (
  <BrowserRouter>
    <Sidebar>
      <PageTransition>
        <Routes>
          {routeConfig.map((route) => (
            <Route
              key={route.path}
              path={route.path}
              element={
                <Suspense fallback={<Loading />}>{route.element}</Suspense>
              }
            />
          ))}
        </Routes>
      </PageTransition>
    </Sidebar>
  </BrowserRouter>
);
