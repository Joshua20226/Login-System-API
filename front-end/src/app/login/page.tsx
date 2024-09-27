"use client";
import { Button, TextField, Typography } from "@mui/material";
import Link from "next/link";
import { useRef, useState, useEffect, FC } from "react";
import { useRouter } from "next/navigation";
import { setCookie } from "nookies";

const Login = () => {
  const router = useRouter();
  const APIURL = process.env.NEXT_PUBLIC_API_URL;
  const [isSignin, setIsSignin] = useState(false);

  const [email, setEmail] = useState("");
  const emailInputRef = useRef<HTMLInputElement>(null);
  const verifyInputRef = useRef<HTMLInputElement>(null);

  // type loginFormType = {
  //   emailInputRef: [React.RefObject<HTMLInputElement>, number];
  // };

  // const loginForm: loginFormType = {
  //   emailInputRef: [emailInputRef, 1],
  // }

  type FormType = {
    inputRef: [React.RefObject<HTMLInputElement>, number];
  };

  const loginForm: FormType = {
    inputRef: [emailInputRef, 1],
  };

  const verifyForm: FormType = {
    inputRef: [verifyInputRef, 1],
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
    let data = { email: emailInput, mode: "signin" };

    try {
      const response = await fetch(APIURL + "/users/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (response.status == 200) {
        setIsSignin(true);
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
      const response = await fetch(APIURL + "/users/signin", {
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
    if (!isSignin) {
      form = loginForm;
    } else {
      form = verifyForm;
    }

    const inputValid = checkRefs(form);
    if (!inputValid) {
      alert("All form has to be filled in.");
      return;
    }

    if (!isSignin) {
      await requestVerificationCode();
    } else {
      await validateCode();
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
        {!isSignin ? (
          <>
            <Typography variant="h5">Login</Typography>

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
        ) : (
          <>
            <Typography variant="h5">Login</Typography>

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

        <Button
          className="p-1"
          variant="contained"
          onClick={() => {
            submitForm();
          }}
        >
          <Typography variant="body2">Submit</Typography>
        </Button>

        <div className="">
          <a href="/sign-up" className="inline-block">
            <Typography variant="body1" className="linkText">
              Sign up
            </Typography>
          </a>
        </div>
      </div>
    </div>
  );
};

export default Login;
