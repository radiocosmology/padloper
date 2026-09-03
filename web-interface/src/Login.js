import axios from 'axios'
import React from 'react'
import ErrorMessage from './ErrorMessage.js';
import { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import GithubIcon from "mdi-react/GithubIcon";
import { OAuthContext } from './contexts/OAuthContext';
import './login.css'
import { withBase, requireOkJson } from './paths.js';

const CLIENT_ID = process.env.REACT_APP_GITHUB_CLIENT_ID || "";

export default function Login() {
    const [rerender, setRerender] = useState(false);
    const [userData, setUserData] = useState({});
    const { accessToken, setAccessToken } = useContext(OAuthContext);

    // Error data to display, if any.
    const [errorData, setErrorData] = useState(null);


    // Forward user to github login screen with client ID. Use login
    // forwarded back with a code like localhost:3000/?code=ASDASDASD; then
    // use the code to get access token.
    useEffect(() => {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const codeParam = urlParams.get('code');

        // TODO: remove local storage
        if (codeParam && (localStorage.getItem("accessToken") === null)) {
            async function getAccessToken() {
                const basePath = (process.env.REACT_APP_BASE_PATH || "/padloper").replace(/\/$/, "");
                const redirectUri = encodeURIComponent(window.location.origin + basePath + "/");
                fetch(withBase(`/oauth/getAccessToken?code=${codeParam}&redirect_uri=${redirectUri}`), {method: "GET"}
                ).then(requireOkJson).then((oauthdata) => {
                    if (oauthdata.access_token) {
                        fetch(withBase(`/oauth/getUserData`), {
                            method: "GET",
                            headers: {"Authorization": "Bearer " + oauthdata.access_token}
                        }).then(requireOkJson).then((userdata) => {
                            axios.post(withBase("/api/login"), {
                                username: userdata.login,
                                accessToken: oauthdata.access_token
                            }).then(res => {
                                // TODO: remove local storage
                                localStorage.setItem("accessToken",
                                                     oauthdata.access_token);
                                setRerender(!rerender);
                                window.location.reload(false);
                            }).catch(err => {
                                console.error(err);
                                setErrorData("Could not sign in. Error was: " +
                                             err.response.data.error);
                            })
                        }).catch(err => {
                            console.error('Failed to get user data:', err);
                            setErrorData('Failed to get user data.');
                        });
                    }
                }).catch(err => {
                    console.error('Failed to obtain access token:', err);
                    setErrorData('Failed to obtain access token.');
                })
            }

//            CONTINUE HERE: figure out whether we need to keep polling the OAuth
//            server for the user information whenever a new page is loaded or
//            whether it can just be done upon login.
            getAccessToken();
        }
    }, []);

    function loginWithGithub() {
      if (!CLIENT_ID) {
        console.error("REACT_APP_GITHUB_CLIENT_ID is not configured");
        alert("GitHub sign-in is not configured. Please set REACT_APP_GITHUB_CLIENT_ID.");
        return;
      }
      const basePath = (process.env.REACT_APP_BASE_PATH || "/padloper").replace(/\/$/, "");
      const redirectUri = encodeURIComponent(window.location.origin + basePath + "/");
      window.location.assign("https://github.com/login/oauth/authorize?client_id=" + CLIENT_ID + "&redirect_uri=" + redirectUri);
    }

    return (
      <div className="App">
        <header className="App-header">
          {/* TODO: remove local storage */}
          {localStorage.getItem("accessToken") ?
          <>
            {Object.keys(userData).length !== 0 ?
            <>
              <h4>Hey there {userData.login}</h4>
              <img width="100px" height="100px" src={userData.avatar_url}/>
              <a href={userData.html_url} style={{"color": "white"}}>Link
                  to GitHub profile</a>
            </>
            :
            <>
            </>
            }
          </>
          :
          <>
            <div className='container'>
              <h3>You must sign in to use this application.</h3>
              <div className='login-container'>
                <a className='login-link' onClick={loginWithGithub}>
                  <GithubIcon />
                  <span>Sign in with GitHub</span>
                </a>
              </div>
              <ErrorMessage style={{marginTop: '10px', marginBottom:'10px'}}
                            errorMessage={errorData}/>
            </div>

          </>
          }
        </header>
      </div>
    );
  }
