import { Routes, Route } from 'react-router-dom'
import { Layout, Questionnaires, Profile, Favorite, Filter } from './pages';
import { FilterProvider } from './contexts/FilterContext';

const App = () => {
  return (
    <FilterProvider>
      <Layout>
        <Routes>
          <Route path='/' element={<Questionnaires />} />
          <Route path='/profile' element={<Profile />} />
          <Route path='/like' element={<Favorite />} />
          <Route path='/filter' element={<Filter />} />
        </Routes>
      </Layout>
    </FilterProvider>
  );
}

export default App;