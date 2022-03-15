import './App.css';

import ComponentList from './ComponentList.js';
import ComponentTypeList from './ComponentTypeList.js';
import ComponentRevisionList from './ComponentRevisionList.js';
import PropertyTypeList from './PropertyTypeList';
import ComponentPage from './ComponentPage.js';
import ComponentConnectionVisualizer from './ComponentConnectionVisualizer.js';
import Header from './Header.js';

import { ReactFlowProvider } from 'react-flow-renderer';

import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";


function App() {

  // return the necessary JSX.
  return (
    <div className="App">
      <Router>

        <Header />

        <Routes>

          <Route 
            exact={true} 
            path="/list/component"
            element={<ComponentList />} 
          />
            
          <Route 
            exact={true} 
            path="/list/component-types"
            element={<ComponentTypeList />} 
          />

          <Route 
            exact={true} 
            path="/list/component-revisions" 
            element={<ComponentRevisionList />}
          />

          <Route 
            exact={true} 
            path="/list/property-types"
            element={
              <PropertyTypeList />
            } 
          />
          
          <Route 
            exact={true} 
            path="/component-connections" 
            element={
              <ReactFlowProvider>
                <ComponentConnectionVisualizer />
              </ReactFlowProvider>
            } 
          />
          
          <Route exact path="/component/:name" element={<ComponentPage />} />

        </Routes>

      </Router>

    </div>
  );
}

export default App;
