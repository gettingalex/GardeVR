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



  // Select all buttons with class 'submitBtn'
var buttons = document.querySelectorAll('.submitBtn');

// Select the modal and the "I Agree" button
var modal = document.getElementById('termsModal');
var agreeBtn = document.getElementById('agreeBtn');

// Loop through each button
buttons.forEach(function(button) {
  // Add click event listener
  button.addEventListener('click', function(event) {
    // Prevent the initial action
    event.preventDefault();

    // Show the modal
    modal.style.display = "block";
  });
});

// When the user clicks on "I Agree", hide the modal and proceed with the initial action
agreeBtn.addEventListener('click', function() {
  modal.style.display = "none";
  window.location.href = button.getAttribute('href');
});



  // Installment event handler
  // const buttonsTwo = document.getElementsByClassName("submitBtn-installment");
  // for(let i = 0; i < buttonsTwo.length; i++) {
  //   buttonsTwo[i].addEventListener("click", function() {
  //     var price_var = this.getAttribute('price_ID'); // 'this' refers to the button that was clicked
  //     fetch('/process_variable', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({product_price: price_var}),
  //     })
  //     .then(response => response.text())
  //     .then(() => {
  //       // Get Checkout Session ID
  //       return fetch("/create-installment-session")
  //     })
  //     .then((result) => { return result.json(); })
  //     .then((data) => {
  //       console.log(data);
  //       // Redirect to Stripe Checkout
  //       return stripe.redirectToCheckout({sessionId: data.sessionId})
  //     })
  //     .then((res) => {
  //       console.log(res);
  //     });
  //   });
  // }