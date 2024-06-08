import React, { useState } from 'react';
import Board from './components/Visual'; 
import './App.css';

  const users_list = [
    {
      uname: "Teacher",
      pass: "1234",
    },
    {
      uname: "Student1",
      pass: "1234",
    },
    {
      uname: "Student2",
      pass: "1234",
    },
    {
      uname: "Student3",
      pass: "1234",
    },
  ]

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [usernameExist, setUsernameExist] = useState(false);
  
  
  const handleUsernameSubmit = () => {
    if (username && password) {
      const user = users_list.find(user => user.uname === username && user.pass === password);
        if (user) {
          setUsernameExist(true);
        } else {
            setError('Incorrect username or password!');
        }
    }
    else {
      setError("Enter username and password!")
    }
  }

  return (
    <div className="App" style={{backgroundImage: "linear-gradient(to right, #d3d1dc, #d3cedc, #d3ccdc, #d3c9dc, #d4c6db, #d2c8e1, #d0cbe6, #ccceeb, #c2d8f4, #b8e2f8, #b4eaf5, #b8f2ee)"}}>
      { username && usernameExist ? (
        <Board username={username} />
      ): (
        <div className="container w-50 p-5" style={{height: "100vh"}}>
          <img src="/images/logo-transparent.png" alt="" className='mb-3'/>
          <div className="mb-3 text-start">
          {error && (
                    <div className="alert alert-danger mb-3 text-danger" role="alert">
                        {error}
                    </div>
                )}
            <label htmlFor="username" className="form-label fs-6 fw-bold">User Name</label>
            <input
              type="text"
              className="form-control mb-4"
              name="username"
              id="username"
              placeholder="username"
              value={username}
              onChange={ (e) => setUsername(e.target.value)}
            />
            <label htmlFor="password" className="form-label fs-6 fw-bold">Password</label>
            <input
              type="password"
              className="form-control mb-4"
              name="password"
              id="password"
              placeholder="password"
              value={password}
              onChange={ (e) => setPassword(e.target.value)}
            />
            <button className='btn btn-success d-block w-100' onClick={handleUsernameSubmit}>Log In</button>
          </div>
          
        </div>
      )
      }
    </div>
  );
}

export default App;