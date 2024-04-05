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
  }
});


// NEW CODE

// Select all buttons with class 'submitBtn'
var buttons = document.querySelectorAll('.submitBtn');

// Variable to store the clicked button's information
var clickedButton;

// Loop through each button
buttons.forEach(function(button) {
  // Add click event listener
  button.addEventListener('click', function(event) {
    // Prevent the initial action
    event.preventDefault();

    // Store the clicked button's information
    clickedButton = button;

    // Redirect to terms.html
    window.location.href = '/termes.html';
  });
});

// When the user clicks on "accept-btn" on termes.html, send a POST request to "/create-checkout-session"
var acceptBtn = document.getElementById('accept-btn');
if (acceptBtn) {
  acceptBtn.addEventListener('click', function() {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/create-checkout-session', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send('product_id=' + clickedButton.getAttribute('product_ID') + '&price_id=' + clickedButton.getAttribute('price_ID') + '&quantity=' + clickedButton.getAttribute('data-quantity'));
  });
}

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




