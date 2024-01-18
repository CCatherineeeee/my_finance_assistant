export const callFlaskEndpoint = async function (
    endpoint,
    isPost = false,
    postData = null
  ) {
    const optionsObj = isPost ? { method: "POST" } : {};
    if (isPost && postData !== null) {
      optionsObj.headers = { "Content-type": "application/json" };
      optionsObj.body = JSON.stringify(postData);
    }
  
    // Assume your Flask backend is running on the same domain and port
    const baseURL = 'http://localhost:5000'; // Change this to your Flask backend URL
    const flaskEndpoint = baseURL + endpoint;
  
    const response = await fetch(flaskEndpoint, optionsObj);
    
    if (response.status === 500) {
      await handleServerError(response);
      return;
    }
  
    const data = await response.json();
    console.log(`Result from calling ${flaskEndpoint}: ${JSON.stringify(data)}`);
    return data;
  };
  