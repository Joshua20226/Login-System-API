
import { cookies } from 'next/headers';
import { NextPage } from 'next';
import { redirect } from 'next/navigation';

type AuthProps = {};

const Auth = <P extends AuthProps>(Component: NextPage<P>): NextPage<P> => {
  
  const AuthenticatedComponent: NextPage<P> = (props) => {
    const cookiesStore = cookies();
    const sessionToken = cookiesStore.get('token');

      if (!sessionToken) {
        redirect('/login');
      }

    return sessionToken ? <Component {...props} /> : null;
  };

  return AuthenticatedComponent;
};

export default Auth;
