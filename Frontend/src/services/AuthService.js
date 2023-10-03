import ApiService from './ApiService'
import store from '../store'
import { onSignOutSuccess, onSignInSuccess, } from '../store/auth/sessionSlice'
import { setUser } from '../store/auth/userSlice'
import { TOKEN_TYPE, REQUEST_HEADER_AUTH_KEY } from 'constants/api.constant'
import { PERSIST_STORE_NAME } from 'constants/app.constant'
import deepParseJson from 'utils/deepParseJson'

/* export async function apiSignIn(data) {
    return ApiService.fetchData({
        url: 'http://127.0.0.1:8000/api/admin/login/',
        method: 'post',
        data,
    })
} */

export async function apiSignIn(data) {
    try {
        const resp = await ApiService.fetchData({
            url: 'http://127.0.0.1:8000/api/admin/login/',
            method: 'post',
            data,
        });

        if (resp.data) {
            const { token, email, userName } = resp.data;

            // Dispatch the onSignInSuccess action with the token
            store.dispatch(onSignInSuccess(token));

            // Optionally, you can set the user data in the store
            store.dispatch(setUser({
                userName,
                email,
            }));


            // Save the userName and email to local storage
            const rawPersistData = localStorage.getItem(PERSIST_STORE_NAME);
            const persistData = deepParseJson(rawPersistData) || {}; // Initialize with an empty object if data is null
            persistData.auth = persistData.auth || {};
            persistData.auth.user = { userName, email };
            localStorage.setItem(PERSIST_STORE_NAME, JSON.stringify(persistData));
        }

        return resp; // Return the full response
    } catch (error) {
        return Promise.reject(error); // Rethrow the error to handle it in your component
    }
}

export async function apiSignUp(data) {
    return ApiService.fetchData({
        url: '/sign-up',
        method: 'post',
        data,
    })
}

export async function apiSignOut() {
    try {
        // Clear local storage
        localStorage.clear();

        // Dispatch the sign-out action
        store.dispatch(onSignOutSuccess());

        // Optionally, you can navigate the user to the sign-in page or any other page.
        //navigate(appConfig.unAuthenticatedEntryPath);
        // For example, if you're using React Router, you can use the navigate function here.
        // import { useNavigate } from 'react-router-dom';
        // const navigate = useNavigate();
        // navigate('/sign-in'); // Replace with the URL of your sign-in page

        return { status: 'success', message: 'Logged out successfully' };
    } catch (error) {
        console.error('Error during sign-out:', error);
        throw error; // Rethrow the error to handle it in your component
    }
}

/* export async function apiSignOut(data) {
    return ApiService.fetchData({
        url: '/sign-out',
        method: 'post',
        data,
    })
} */

export async function apiForgotPassword(data) {
    return ApiService.fetchData({
        url: '/forgot-password',
        method: 'post',
        data,
    })
}

export async function apiResetPassword(data) {
    return ApiService.fetchData({
        url: '/reset-password',
        method: 'post',
        data,
    })
}
