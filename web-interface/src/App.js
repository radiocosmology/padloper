import './App.css';

import ComponentList from './ComponentList.js';
import ComponentTypeList from './ComponentTypeList.js';
import ComponentRevisionList from './ComponentRevisionList.js';
import ComponentPage from './ComponentPage.js';
import Header from './Header.js';

import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";

function App() {

  // return the necessary JSX.
  return (
    <div className="App">
      <Router>

        <Header />

        <Switch>
          <Route exact={true} path="/list/component">
            <ComponentList />
          </Route>
          <Route exact={true} path="/list/component-types">
            <ComponentTypeList />
          </Route>
          <Route exact={true} path="/list/component-revisions">
            <ComponentRevisionList />
          </Route>
          
          <Route exact path="/component/:name">
            <ComponentPage />
          </Route>
        </Switch>

      </Router>

    </div>
  );
}

export default App;
