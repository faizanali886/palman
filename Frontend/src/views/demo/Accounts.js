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

const Accounts = () => {
    //const endpoint = 'http://3.88.116.254';
    const endpoint = 'http://127.0.0.1:8000';
    const [bots, setBots] = useState([]);

    const [showSidebar, setShowSidebar] = useState(false);

    const [formData, setFormData] = useState({
        apiSecret: '',
        botNumber: '',
        botLanguage: '',
        botSpeaker: '',
        maxUser: '',
        botid: '',
        phone: '',
    });

    useEffect(() => {
        axios.get(`${endpoint}/api/bots/`)
            .then(response => {
                setBots(response.data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }, []);

    const toggleSidebar = () => {
        setShowSidebar(!showSidebar);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value,
        });

    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const formDataWithNumberBotId = {
            ...formData,
            botid: parseInt(formData.botid),
            maxUser: parseInt(formData.maxUser) // Convert to number
        };


        axios.post(`${endpoint}/api/bots/`, formDataWithNumberBotId)
            .then(response => {
                // Handle successful response here, e.g., show a success message or update the bot list
                console.log('Bot created successfully:', response.data);
                alert('New Bot added');
                window.location.reload();
                setShowSidebar(false);
            })
            .catch(error => {
                // Handle error here, e.g., display an error message
                console.error('Error creating bot:', error);

                // Check if the error response contains a custom error message
                if (error.response && error.response.data && error.response.data.botid) {
                    alert('Error creating bot: ' + error.response.data.botid[0]); // Display the error message
                } else {
                    alert('Error creating bot. Please try again later.'); // Default error message
                }
            });
    };

    return (
        <div className="flex flex-col">
            <h1 className='text-4xl font-medium leading-tight text-primary'>Bot Accounts</h1>
            <br />

            <div className="ml-auto mr-auto bg-primary px-4 py-2 text-sm font-medium uppercase leading-normal">
                <Button

                    block


                    variant="solid"
                    onClick={toggleSidebar}
                >
                    Add Bot
                </Button>
            </div>

            <div className={`overflow-y-auto fixed inset-y-0 right-0 z-50 w-64 bg-white shadow-lg transform ${showSidebar ? 'translate-x-0' : 'translate-x-full'} transition-transform duration-300 ease-in-out`}>
                <div className="p-4">
                    <h2 className="text-2xl font-semibold mb-4">Create Bot</h2>

                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">API Secret</label>
                            <input
                                type="text"
                                name="apiSecret"
                                value={formData.apiSecret}
                                onChange={handleChange}
                                className="mt-1 p-2 border rounded-md w-full"
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Bot Number</label>
                            <input
                                type="text"
                                name="botNumber"
                                value={formData.botNumber}
                                onChange={handleChange}
                                className="mt-1 p-2 border rounded-md w-full"
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Bot Language</label>
                            <input
                                type="text"
                                name="botLanguage"
                                value={formData.botLanguage}
                                onChange={handleChange}
                                className="mt-1 p-2 border rounded-md w-full"
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Bot Speaker</label>
                            <input
                                type="text"
                                name="botSpeaker"
                                value={formData.botSpeaker}
                                onChange={handleChange}
                                className="mt-1 p-2 border rounded-md w-full"
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Max User</label>
                            <input
                                type="text"
                                name="maxUser"
                                value={formData.maxUser}
                                onChange={handleChange}
                                className="mt-1 p-2 border rounded-md w-full"
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Bot ID</label>
                            <input
                                type="text"
                                name="botid"
                                value={formData.botid}
                                onChange={handleChange}
                                className="mt-1 p-2 border rounded-md w-full"
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">Phone</label>
                            <input
                                type="text"
                                name="phone"
                                value={formData.phone}
                                onChange={handleChange}
                                className="mt-1 p-2 border rounded-md w-full"
                                required
                            />
                        </div>


                        <Button
                            block

                            variant="solid"
                            type="submit"

                        >
                            Create Bot

                        </Button>
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




            <div className="overflow-x-auto sm:-mx-6 lg:-mx-8">
                <div className="inline-block min-w-full max-w-screen-lg">
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-left text-sm font-light">
                            <thead className="border-b font-medium dark:border-neutral-500">
                                <tr>
                                    <th scope="col" className="px-6 py-4">#</th>
                                    <th scope="col" className="px-6 py-4">API Secret</th>
                                    <th scope="col" className="px-6 py-4">Bot ID</th>
                                    <th scope="col" className="px-6 py-4">Bot Language</th>
                                    <th scope="col" className="px-6 py-4">Bot Speaker</th>
                                    <th scope="col" className="px-6 py-4">Max User</th>
                                    <th scope="col" className="px-6 py-4">Bot Number</th>
                                    <th scope="col" className="px-6 py-4">Phone</th>
                                </tr>
                            </thead>
                            <tbody>
                                {bots.map(bot => (
                                    <tr
                                        key={bot.id}
                                        className="border-b transition duration-300 ease-in-out hover:bg-neutral-100 dark:border-neutral-500 dark:hover:bg-neutral-600"
                                    >
                                        <td className="whitespace-nowrap px-6 py-4 font-medium">{bot.id}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{bot.apiSecret}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{bot.botid}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{bot.botLanguage}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{bot.botSpeaker}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{bot.maxUser}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{bot.botNumber}</td>
                                        <td className="whitespace-nowrap px-6 py-4">{bot.phone}</td>
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

export default Accounts;
