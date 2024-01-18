import { callFlaskEndpoint } from "./utils.js";

let linkTokenData;
let publicTokenToExchange;

async function initializeLink() {
  try {
    const response = await fetch("http://127.0.0.1:5000/server/create_link_token");

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const linkTokenData = await response.json();
    // Now you can use linkTokenData as needed
    console.log(linkTokenData);
  } catch (error) {
    // Handle errors
    console.error('Error during fetch operation:', error);
  }
}

const startLink = function () {
  console.log("triggered start link function")
  if (linkTokenData === undefined) {
    return;
  }
  const handler = Plaid.create({
    token: linkTokenData.link_token,
    onSuccess: async (publicToken, metadata) => {
      console.log(`ONSUCCESS: Metadata ${JSON.stringify(metadata)}`);
      showOutput(
        `I have a public token: ${publicToken} I should exchange this`
      );
      publicTokenToExchange = publicToken;
      document.querySelector("#exchangeToken").removeAttribute("disabled");
    },
    onExit: (err, metadata) => {
      console.log(
        `Exited early. Error: ${JSON.stringify(err)} Metadata: ${JSON.stringify(
          metadata
        )}`
      );
      showOutput(`Link existed early with status ${metadata.status}`)
    },
    onEvent: (eventName, metadata) => {
      console.log(`Event ${eventName}, Metadata: ${JSON.stringify(metadata)}`);
    },
  });
  handler.open();
};

document.querySelector(initializeLink).addEventListener("click", initializeLink)

const selectorsAndFunctions = {
  "#initializeLink": initializeLink,
  "#startLink": startLink,
  // "#exchangeToken": exchangeToken,
  // "#getAccountsInfo": getAccountsInfo,
  // "#getItemInfo": getItemInfo,
};

Object.entries(selectorsAndFunctions).forEach(([sel, fun]) => {
  if (document.querySelector(sel) == null) {
    console.warn(`Hmm... couldn't find ${sel}`);
  } else {
    document.querySelector(sel)?.addEventListener("click", fun);
  }
});