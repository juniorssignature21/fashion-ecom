import Swal from  './node_modules/sweetalert2/src/sweetalert2.js';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


$(document).ready(function() {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
    });

    function generateCartId() {
        const Is_cartid = localStorage.getItem('cartId');

        if (Is_cartid === null) {
            var cartId = "";
            for (var i = 0; i < 10; i++) {
                cartId += Math.floor(Math.random() * 10);
            }

            localStorage.setItem('cartId', cartId);
        }
        return Is_cartid || cartId;
    }
    function syncCartCount() {
        const cart_id = localStorage.getItem('cartId');
        if (cart_id) {
            $.ajax({
                url: '/get-cart-count/',
                method: 'GET',
                data: { 'cart_id': cart_id },
                success: function(response) {
                    $('.total_cart_items').text(response.total_cart_items);
                    $('.price').text(`₦ ${response.cart_sub_total}`);
                    $('.total_price').text(`₦ ${response.total_price}`);
                }
            });
        }
    }

    // 2. Run it immediately on page load
    syncCartCount();

    // Handle Increment
    $(document).on('click', '.plus', function() {
        let input = $(this).siblings('.qty-input');
        let val = parseInt(input.val());
        let max = parseInt(input.attr('max'));
        if (val < max) {
            input.val(val + 1);
        } else {
            input.val(max);
        }
    });

    // Handle Decrement
    $(document).on('click', '.minus', function() {
        let input = $(this).siblings('.qty-input');
        let val = parseInt(input.val());
        if (val > 1) {
            input.val(val - 1);
        }
    });

     
    $(document).on('click', '.add-to-cart-btn', function() {
        const button_el = $(this);
        const id = button_el.attr("data-id");
        // const qty = $("input.quantity").val();
        // This finds the input inside the same parent container
        const qty = button_el.siblings('.qty-container').find('.qty-input').val();
        const size = $("input[name='size']:checked").val();
        const color = $("input[name='color']:checked").val();
        const cart_id = generateCartId();

        $.ajax({
            url: '/add-to-cart/',
            data: {
                'id': id,
                'qty': qty,
                'size': size,
                'color': color,
                'cart_id': cart_id,
            },
            beforeSend: function() {
                button_el.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...');
                button_el.prop('disabled', true);
            },
            success: function(response) {
                console.log(response);

                Toast.fire({
                    icon: 'success',
                    title: response.message,
                });
                button_el.html('Add to Cart');
                button_el.prop('disabled', false);

                $('.total_cart_items').text(response?.total_cart_items);
            },
            error: function(xhr, status, error) {
                console.error("Error Status:", xhr.status);
                console.error("Error Response:", xhr.responseText);

                let errorResponse = JSON.parse(xhr.responseText);

                Toast.fire({
                    icon: 'error',
                    title: errorResponse?.error,
                });

            }
        });

    });

    //update cart quantity
    $(document).on('click', '.qtybtn', function(){
        const button_el = $(this);
        // const update_type = button_el.attr('data-update-type');
        const item_id = button_el.attr('data-item-id');
        let qty = parseInt($("input.item-qty-" + item_id).val());
        const product_id = button_el.attr('data-product-id');
        
        const cart_id = generateCartId();
        const stock = parseInt($("input.item-qty-" + item_id).attr('data-qty')); // Get stock from data attribute
        
        if (button_el.hasClass('inc')) {
            var newVal = parseInt(qty) + 1;

        } else {
            // Don't allow decrementing below zero
            if (qty > 0) {
                var newVal = parseInt(qty) - 1;
            } else {
                newVal = 0;
            }
        }

        qty = parseInt(newVal);

        // Proceed with the AJAX call if the quantity is within stock limits
        $.ajax({
            url: "/add-to-cart/",
            data: {
                id: product_id,
                qty: qty,
                cart_id: cart_id,
            },
            // beforeSend: function () {
            //     button_el.html("<i class='fa fa-spinner fa-spin ms-2'></i>");
            // },
            success: function(response) {
                console.log(response);
                Toast.fire({
                    icon: "success",
                    title: response?.message,
                });

                setTimeout(() => {
                    location.reload();
                }, 1500); // adjust time to match toast duration

                $(".item_sub_total_" + item_id).text(response.item_sub_total);
                $(".cart_sub_total").text(response.cart_sub_total);
                $(".total_price").text(response.total_price);
                // button_el.html("<i class='fa fa-edit'></i>");
                // refresh page
            },
            error: function(xhr, status, error) {
                console.log("Error Status: ", xhr.status);
                console.log("Response Text: ", xhr.responseText);
                let errorResponse = JSON.parse(xhr.responseText);
                Toast.fire({
                    icon: "error",
                    title: errorResponse?.error,
                });
                // Reset quantity input and button text on error
                $(".item-qty-" + item_id).val(stock); // Set input value to stock limit
                $(".total_price").text(response.total_price);
                
                // if (update_type === "increase") {
                //     button_el.html("<i class='fa fa-plus'></i>");
                // } else {
                //     button_el.html("<i class='fa fa-minus'></i>");
                // }
            }
        });

        // window.location.reload();

    });
    
    //delete item from cart
    $(document).on('click', '.delete_cart_item', function(){
        const button_el = $(this);
        const item_id = button_el.attr('data-item-id');
        const product_id = button_el.attr('data-product-id');
        const cart_id = generateCartId();

        $.ajax({
            url: "/delete-cart-item/",
            data: {
                id: product_id,
                item_id: item_id,
                cart_id: cart_id,
            },

            beforeSend: function () {
                button_el.html("<i class='fa fa-spinner fa-spin ms-2'></i>");
            },
            success: function(response){
                console.log(response)
                Toast.fire({
                    icon: "success",
                    title: response?.message,
                });
                $(".total_cart_items").text(response?.total_cart_items);
                $(".cart_sub_total").text(response?.cart_sub_total);
                $(".item_div_" + item_id).addClass("d-none");
                button_el.html("<i class='fa fa-close'></i>");
                window.location.reload();
            },
        });
    });

    $(document).on('click', '.add_to_wishlist', function(){
        const button = $(this);
        const product_id = button.attr("data-product_id");
        console.log(product_id);

        $.ajax({
            url: `/customers/add_to_wishlist/${product_id}/`,
            beforeSend: function () {
                button.html("<i class='fas fa-spinner fa-spin text-grey'></i>");
            },

            success: function(response){
                button.html("<i class='far fa-heart'></i>");
                console.log(response);

                if (response.message === "User is not logged in"){
                    Toast.fire({
                        icon: "warning",
                        title: response.message,
                        
                    });

                } else {
                    Toast.fire({
                        icon: "success",
                        title: response.message,
                        
                    });
                };
            },
            error: function(){
                button.html("<i class='far fa-heart'></i>");
            }

        });

    });
    
    document.querySelectorAll('.address-btn').forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('.address');
            const button_el = $(this);
            const radio = container.querySelector('input[type="radio"]');

            radio.checked = true;
            document.querySelectorAll('.address').forEach(box => {
                box.classList.remove('active');
            
            });
            container.classList.add('active');
            
        });
    });
    
});