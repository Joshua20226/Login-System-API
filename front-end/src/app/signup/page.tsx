"use client";
import { Button, TextField, Typography } from "@mui/material";
import Link from "next/link";
import { useRef, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { setCookie } from "nookies";

const Signup = () => {
  const router = useRouter();
  const APIURL = process.env.NEXT_PUBLIC_API_URL;
  const [isSignup, setIsSignup] = useState(false);
  const [isVerified, setIsVerified] = useState(false);
  const [email, setEmail] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const emailInputRef = useRef<HTMLInputElement>(null);
  const verifyInputRef = useRef<HTMLInputElement>(null);
  const usernameInputRef = useRef<HTMLInputElement>(null);

  type FormType = {
    inputRef: [React.RefObject<HTMLInputElement>, number];
  };

  const loginForm: FormType = {
    inputRef: [emailInputRef, 1],
  };

  const verifyForm: FormType = {
    inputRef: [verifyInputRef, 1],
  };

  const usernameForm: FormType = {
    inputRef: [usernameInputRef, 1],
  };

  const checkRefs = (form: FormType) => {
    for (const [key, [ref, number]] of Object.entries(form)) {
      if (number === 1) {
        if (
          ref.current?.value === null ||
          ref.current?.value === "" ||
          ref.current?.value === undefined
        ) {
          return false;
        } else {
          console.log(ref.current?.value, number);
        }
      }
    }

    return true;
  };

  //   Email & Mode
  const requestVerificationCode = async () => {
    let emailInput: string = emailInputRef.current?.value ?? "";
    let data = { email: emailInput, mode: "signup" };

    try {
      const response = await fetch(APIURL + "/users/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (response.status == 200) {
        setIsSignup(true);
        setEmail(emailInput);
      }

      const result = await response.json();
      alert(result.message);
    } catch (error) {
      console.error("There was an error!", error);
    }
  };

  //   Email & Verification Code
  const validateCode = async () => {
    let verifyInput: string = verifyInputRef.current?.value ?? "";
    let data = { email: email, verification_code: verifyInput };

    try {
      const response = await fetch(APIURL + "/users/signup/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (response.status == 200) {
        setIsVerified(true);
        setIsSignup(false);
        setVerificationCode(verifyInput);
      }

      const result = await response.json();
      alert(result.message);
    } catch (error) {
      console.error("There was an error!", error);
    }
  };

  //   Email & Verification Code & Username
  const submitUsername = async () => {
    let usernameInput: string = usernameInputRef.current?.value ?? "";
    let data = {
      email: email,
      username: usernameInput,
      verification_code: verificationCode,
    };

    try {
      const response = await fetch(APIURL + "/users/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      alert(result.message);

      console.log(result.access_token, result.refresh_token);
      if (response.status == 200) {
        // Store refresh and access token to storage
        // Store tokens in cookies
        setCookie(null, "accessToken", result.access_token, {
          maxAge: 60 * 15, // 15 minutes
          path: "/",
        });

        const tokenResponse = await fetch("/api/store-refresh-token", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh_token: result.refresh_token }),
        });

        router.push("/user");
      }
    } catch (error) {
      console.error("There was an error!", error);
    }
  };

  const submitForm = async () => {
    let form: FormType;
    if (!isSignup && !isVerified) {
      form = loginForm;
    } else if (isSignup) {
      form = verifyForm;
    } else if (isVerified) {
      form = usernameForm;
    } else {
      form = loginForm;
    }

    const inputValid = checkRefs(form);
    if (!inputValid) {
      alert("All form has to be filled in.");
      return;
    }

    if (!isSignup && !isVerified) {
      await requestVerificationCode();
    } else if (isSignup) {
      await validateCode();
    } else if (isVerified) {
      await submitUsername();
    }
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submitForm();
    }
  };

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  });

  return (
    <div className="flex items-center justify-center p-10">
      <div className="grid gap-6 p-10 border-2 border-gray-300 rounded-xl">
        {/* Ask for gmail */}
        {!isSignup && !isVerified && (
          <>
            <Typography variant="h5">Sign Up</Typography>

            <div>
              <Typography variant="body1">Email</Typography>
              <TextField
                variant="outlined"
                label="Enter Title"
                type="text"
                inputRef={emailInputRef}
              />
            </div>
          </>
        )}

        {/* Ask for verification code */}
        {isSignup && (
          <>
            <Typography variant="h5">Sign Up</Typography>

            <div>
              <Typography variant="body1">Verification Code</Typography>
              <TextField
                variant="outlined"
                label="Enter Title"
                type="text"
                inputRef={verifyInputRef}
              />
            </div>
          </>
        )}

        {/* Ask for username */}
        {isVerified && (
          <>
            <Typography variant="h5">Sign Up</Typography>

            <div>
              <Typography variant="body1">Username</Typography>
              <TextField
                variant="outlined"
                label="Enter Title"
                type="text"
                inputRef={usernameInputRef}
              />
            </div>
          </>
        )}

        <Button
          className="p-1"
          variant="contained"
          onClick={() => {
            submitForm();
          }}
        >
          <Typography variant="body2">Submit</Typography>
        </Button>
      </div>
    </div>
  );
};

export default Signup;
