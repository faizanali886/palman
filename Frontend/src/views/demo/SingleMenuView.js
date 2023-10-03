import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Input,
    Button,
    Checkbox,
    FormItem,
    FormContainer,
    Alert,
} from 'components/ui'
import { windowScroll } from '@tanstack/react-virtual';

const SingleMenuView = () => {
    const [users, setUsers] = useState([]);
    const [showSidebar, setShowSidebar] = useState(false);
    const [formData, setFormData] = useState({
        number: '',
        name: '',
        email: '',
        //consumed_credits: '',
        initial_credits: '',
        //remaining_credits: '',
        status: '',
        //location: '',
        botid: 0,
    });

    const [botIds, setBotIds] = useState([]);
    //const endpoint = 'http://3.88.116.254';
    const endpoint = 'http://127.0.0.1:8000';

    useEffect(() => {
        axios.get(`${endpoint}/api/users/`)
            .then(response => {
                setUsers(response.data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });

        // Fetch bot data and extract botid values
        axios.get(`${endpoint}/api/bots/`)
            .then(response => {
                const botData = response.data;
                const botIdsArray = botData.map(bot => bot.botid);
                setBotIds(botIdsArray);
            })
            .catch(error => {
                console.error('Error fetching bot data:', error);
            });

    }, []);

    // Function to toggle the sidebar
    const toggleSidebar = () => {
        setShowSidebar(!showSidebar);
    };

    // Function to handle form input changes
    const handleInputChange = event => {
        const { name, value } = event.target;
        setFormData({
            ...formData,
            [name]: value,
        });
    };

    // Function to handle form submission
    const handleSubmit = event => {
        event.preventDefault();
        const formDataWithNumberBotId = {
            ...formData,
            botid: parseInt(formData.botid), // Convert to number
        };
        // Send a POST request to the API with formData
        axios.post(`${endpoint}/api/users/`, formDataWithNumberBotId, {
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => {
                // Handle success, e.g., display a success message
                //console.log('User created successfully:', response.data);
                // You may want to update the users list with the new data here
                // setUsers([...users, response.data]);
                // Close the sidebar
                alert('New User is added!')
                window.location.reload();
                setShowSidebar(false);
            })
            .catch(error => {
                // Handle error, e.g., display an error message
                console.error('Error creating user:', error);
                if (error.response && error.response.data && error.response.data.number) {
                    alert('Error creating user: ' + error.response.data.number); // Display the error message
                } else {
                    alert('Error creating user. Please try again later.'); // Default error message
                }
            });
    };

    return (
        <div className="flex flex-col">
            <h1 className='text-4xl font-medium leading-tight text-primary'>Users</h1>
            <br />

            {/* Button aligned to the right */}

            <div className="ml-auto mr-auto bg-primary px-4 py-2 text-sm font-medium uppercase leading-normal">
                <Button

                    block


                    variant="solid"
                    onClick={toggleSidebar}
                >
                    Add User
                </Button>
            </div>


            {/* Collapsible Sidebar */}
            <div className={`overflow-y-auto fixed inset-y-0 right-0 z-50 w-64 bg-white shadow-lg transform ${showSidebar ? 'translate-x-0' : 'translate-x-full'} transition-transform duration-300 ease-in-out`}>
                <div className="p-4">
                    <h2 className="text-2xl font-semibold mb-4">Create User</h2>
                    {/* Form for creating a new user */}
                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Number</label>
                            <input
                                type="text"
                                name="number"
                                value={formData.number}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Name</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Email</label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div>
                        {/*  <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Consumed Credits</label>
                            <input
                                type="text"
                                name="consumed_credits"
                                value={formData.consumed_credits}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div> */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Initial Credits</label>
                            <input
                                type="text"
                                name="initial_credits"
                                value={formData.initial_credits}
                                placeholder='hr:min:sec'
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div>
                        {/*  <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Remaining Credits</label>
                            <input
                                type="text"
                                name="remaining_credits"
                                value={formData.remaining_credits}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div> */}
                        {/* <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Status</label>
                            <input
                                type="text"
                                name="status"
                                value={formData.status}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div> */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Status</label>
                            <select
                                name="status"
                                value={formData.status}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            >
                                <option value="freetrial">Free Trial</option>
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                                <option value="blocked">Blocked</option>
                            </select>
                        </div>

                        {/* <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Location</label>
                            <input
                                type="text"
                                name="location"
                                value={formData.location}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div> */}
                        {/* <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Bot ID</label>
                            <input
                                type="text"
                                name="botid"
                                value={formData.botid}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            />
                        </div> */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Bot ID</label>
                            <select
                                name="botid"
                                value={formData.botid}
                                onChange={handleInputChange}
                                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                            >
                                <option value="">Select Bot ID</option>
                                {botIds.map(botId => (
                                    <option key={botId} value={botId}>
                                        {botId}
                                    </option>
                                ))}
                            </select>
                        </div>



                        <div className="mt-6">


                            <Button
                                block

                                variant="solid"
                                type="submit"

                            >
                                Create User

                            </Button>


                        </div>
                    </form>
                    <Button className='mt-2 !bg-red-500'

                        block


                        variant="solid"
                        onClick={(e) => { setShowSidebar(false) }}
                    >
                        Close
                    </Button>
                </div>
            </div>

            {/* Main content */}
            <div className="overflow-x-auto sm:-mx-6 lg:-mx-8">
                <div className="inline-block min-w-full py-2 sm:px-6 lg:px-8">
                    <div className="overflow-hidden">
                        <table className="min-w-full text-left text-sm font-light">
                            <thead className="border-b font-medium dark:border-neutral-500">
                                <tr>
                                    <th scope="col" className="px-6 py-4">#</th>
                                    <th scope="col" className="px-6 py-4">Number</th>
                                    <th scope="col" className="px-6 py-4">Name</th>
                                    <th scope="col" className="px-6 py-4">Email</th>
                                    <th scope="col" className="px-6 py-4">Consumed Credits</th>
                                    <th scope="col" className="px-6 py-4">Initial Credits</th>
                                    <th scope="col" className="px-6 py-4">Remaining Credits</th>
                                    <th scope="col" className="px-6 py-4">Status</th>
                                    <th scope="col" className="px-6 py-4">Location</th>
                                    <th scope="col" className="px-6 py-4">Bot ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(user => (
                                    <tr
                                        key={user.id}
                                        className="border-b transition duration-300 ease-in-out hover:bg-neutral-100 dark:border-neutral-500 dark:hover:bg-neutral-600"
                                    >
                                        <td className="whitespace-nowrap px-6 py-4 font-medium">{user.id}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.number}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.name}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.email}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.consumed_credits}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.initial_credits}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.remaining_credits}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.status}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.location}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{user.botid}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default SingleMenuView;
