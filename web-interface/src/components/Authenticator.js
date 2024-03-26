import React from 'react'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom';

export default function Authenticator() {
    const navigate = useNavigate();

    // check if logged in
    useEffect(() => {
        if (!localStorage.getItem("accessToken")) {
            navigate('/');
        }
    }, [])

    return (
    <>
    </>
    )
}
