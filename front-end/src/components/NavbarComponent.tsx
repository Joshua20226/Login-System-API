'use client';

import { Button, Typography } from '@mui/material';
import { useRouter } from 'next/navigation';

const NavbarComponent = () => {

    const router = useRouter();

    const navigation = (path: string) => {
        router.push(path);
    }

    const login = () => {

    };

    // Check whether a session code is stored in cookie
    // If exists, show button for dashboard
    // If doesn't exist, show login button
    const validateLogin = () => {

    }

    validateLogin();

    return (
        <div className='flex justify-center m-4 mt-8 gap-4'>
            <Button className='p-2 ' variant="contained" onClick={() => {navigation('/')}}>
                <Typography variant='body2'>Home</Typography>
            </Button>

            <Button className='p-2 ' variant="contained" onClick={() => {navigation('/login')}}>
                <Typography variant='body2'>Login</Typography>
            </Button>
        </div>
    )
}

export default NavbarComponent
