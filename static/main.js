console.log("Main.js loaded");

document.addEventListener("DOMContentLoaded", function() {
  // Select all buttons with class 'submitBtn'
  var buttons = document.querySelectorAll('.submitBtn');
  // Loop through each button
  buttons.forEach(function(button) {
      // Get the stock quantity from the 'data-quantity' attribute
      var quantity = button.getAttribute('data-quantity');
      console.log(quantity)
      // Check if the quantity is 0
      if(quantity == 0) {
          // Update the button text and disable it
          button.textContent += " n'est plus disponible";
          button.disabled = true;
      }
  });
});

// Get Stripe publishable key
fetch("/config")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

  // Event handler: full price
  const buttonsOne = document.getElementsByClassName("submitBtn");
  for(let i = 0; i < buttonsOne.length; i++) {
    buttonsOne[i].addEventListener("click", function() {
      var price_var = this.getAttribute('price_ID'); // 'this' refers to the button that was clicked
      var product_id = this.getAttribute('product_ID');
      var quantity = this.getAttribute('data-quantity');
      if(quantity == 0) {
        // Update the button text and disable it
        this.textContent += " n'est plus disponible";
        this.disabled = true;
      }
      window.location.href = '/termes?product_id=' + product_id + '&price_id=' + price_var + '&quantity=' + quantity;
  
    }
  )};
});

fetch("/config")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

  // Event handler: accept terms
  const acceptBtn = document.getElementById('accept-btn');
  if (acceptBtn) {
    acceptBtn.addEventListener("click", function() {
      //const urlParams = new URLSearchParams(window.location.search);
      //const product_id = urlParams.get('product_id');
      //const price_id = urlParams.get('price_id');
      //const quantity = urlParams.get('quantity');
      var price_var = this.getAttribute('price_ID'); // 'this' refers to the button that was clicked
      var product_id = this.getAttribute('product_ID');
      var quantity = this.getAttribute('data-quantity');

      fetch('/process_variable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({product_price: price_var, product_ID: product_id}),
      })
      .then(response => response.text())
      .then(() => {
        // Get Checkout Session ID
        return fetch("/create-checkout-session")
      })
      .then((result) => { return result.json(); })
      .then((data) => {
        console.log(data);
        // Redirect to Stripe Checkout
        return stripe.redirectToCheckout({sessionId: data.sessionId})
      })
      .then((res) => {
        console.log(res);
      });
    });
  };
});





