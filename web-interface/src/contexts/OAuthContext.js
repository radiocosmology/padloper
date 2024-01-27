import { useState } from "react";
import { createContext } from "react";

export const OAuthContext = createContext({
    accessToken: "",
    setAccessToken: () => {},
});

export const useOAuthContext = () => {
    const [accessToken, setAccessToken] = useState("")

    return {
        accessToken, setAccessToken,
    }
}