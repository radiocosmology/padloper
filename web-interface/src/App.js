import ComponentList from './ComponentList.js';
import ComponentTypeList from './ComponentTypeList.js';
import ComponentVersionList from './ComponentVersionList.js';
import PropertyTypeList from './PropertyTypeList';
import ComponentPage from './ComponentPage.js';
import ComponentConnectionVisualizer from './ComponentConnectionVisualizer.js';
import FlagTypeList from './FlagTypeList.js'
import FlagList from './FlagList.js';
import Header from './Header.js';

import { ReactFlowProvider } from 'reactflow';

import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";
import Login from './Login.js';
import { OAuthContext, useOAuthContext } from './contexts/OAuthContext.js';
import UserManagementPage from './UserManagement.js';
import UserGroupManagementPage from './UserGroupManagement.js';
import UserCreatePage from './UserCreate.js';

/**
 * The main page where the header and site contents are rendered,
 * depending on the URL's path and parameters.
 */
function App() {

  /**
   * Using React Router for the multi-page functionality. If the path of the
   * URL matches one of the paths below, it will display its corresponding
   * component, giving the multi-page behaviour.
   */

  window.addEventListener("error", (e) => {
    if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || e.message === 'ResizeObserver loop limit exceeded') {
      console.log("Oh, yeah!!!!");
//      e.stopImmediatePropagation();
    }
  });
  // if (localStorage.getItem("accessToken") === null) {
  //   return(
  //     <Login />
  //   );
  // }

  return (
    <OAuthContext.Provider value={useOAuthContext()}>
      <div className="App">

      <Router>
        {/* {localStorage.getItem("accessToken") === null ?
        <></> :
        <Header />
      } */}
        <Header />
        
        <Routes>

          {/**
           * the exact parameter assures that this page will only be shown
           * if the path is matched exactly.
          */}
          <Route
            exact={false}
            path="/"
            element={<Login />}
          />

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
            path="/list/flag-types"
            element={<FlagTypeList />} 
          />

          <Route 
            exact={true} 
            path="/list/flag"
            element={<FlagList />} 
          />

          <Route 
            exact={true} 
            path="/list/component-versions" 
            element={<ComponentVersionList />}
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
            path="/manage/users"
            element={
              <UserManagementPage />
            }
          />


          <Route 
            exact={true}
            path="/manage/users/groups"
            element={
              <UserGroupManagementPage />
            }
          />

          <Route 
            exact={true}
            path="/users"
            element={
              <UserCreatePage />
            }
          />

         

          {
            /**
             * A ReactFlowProvider is wrapped around the visualizer to
             * give it access to the React Flow hooks:
             * https://reactflow.dev/docs/api/react-flow-provider/
             */
          }
          <Route 
            exact={true} 
            path="/component-connections" 
            element={
              <ReactFlowProvider>
                <ComponentConnectionVisualizer />
              </ReactFlowProvider>
            } 
          />
          
          {/*
            :name denotes a URL parameter, so /component/COMP-1 will load
            the component page for COMP-1.
          */}
          <Route exact path="/component/:name" element={<ComponentPage />} />

        </Routes>

      </Router>

      </div>

    </OAuthContext.Provider>
    
  );
}

export default App;
