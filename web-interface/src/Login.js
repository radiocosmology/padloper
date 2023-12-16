import React from 'react'
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import GithubIcon from "mdi-react/GithubIcon";
import './login.css'

const CLIENT_ID = "";

export default function Login() {
    const [rerender, setRerender] = useState(false);
    const [userData, setUserData] = useState({});
    // const navigate = useNavigate();

  
    // forward user to github login screen with client ID
    // use log in
    // forwarded back with a code like localhost:3000/?code=ASDASDASD
    // use code to get access token
  
    useEffect(() => {
      const queryString = window.location.search;
      const urlParams = new URLSearchParams(queryString);
      const codeParam = urlParams.get('code');
      console.log(codeParam);
  
      if (codeParam && (localStorage.getItem("accessToken") === null)) {
        async function getAccessToken() {
          await fetch("http://localhost:4000/getAccessToken?code=" + codeParam, {
            method: "GET"
          }).then((response) => {
            return response.json();
          }).then((data) => {
            console.log(data);
            if (data.access_token) {
              localStorage.setItem("accessToken", data.access_token);
              setRerender(!rerender);
              window.location.reload(false);
            } 
          })
        }
        getAccessToken();
      }
    }, []);
  
    // async function getUserData() {
    //   await fetch("http://localhost:4000/getUserData", {
    //     method: "GET",
    //     headers: {
    //       "Authorization": "Bearer " + localStorage.getItem("accessToken")
    //     }
    //   }).then((response) => {
    //     return response.json();
    //   }).then((data) => {
    //     console.log(data);
    //     setUserData(data);
    //   });
    // }
  
    function loginWithGithub() {
      window.location.assign("https://github.com/login/oauth/authorize?client_id=" + CLIENT_ID);
    }
  
  
    return (
      <div className="App">
        <header className="App-header">
          {localStorage.getItem("accessToken") ? 
          <>
            {/* <h1>We have the access token</h1> */}
            {/* <button onClick={() => { localStorage.removeItem("accessToken"); setRerender(!rerender); window.location.reload(false); }}>
              Log out
            </button>  */}
            {/* <h3>Get User Data from GitHub API</h3> */}
            {/* <button onClick={getUserData}>Get Data`</button> */}
            {Object.keys(userData).length !== 0 ?
            <>
              <h4>Hey there {userData.login}</h4>
              <img width="100px" height="100px" src={userData.avatar_url}/>
              <a href={userData.html_url} style={{"color": "white"}}>Link to GitHub profile</a>
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
            <a
              className='login-link'
              onClick={loginWithGithub}
            >
              <GithubIcon />
              <span>Sign in with GitHub</span>
            </a>
            {/* <button onClick={loginWithGithub}>
              Login with GitHub
            </button> */}
            </div>
            </div>
          </>
          }
        </header>
      </div>
    );
  }
