console.log("goooooooooooooodddddddddddd gooiiinnnnnnnnnnnnnnnnggggggg");

const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sept","Oct","Nov","Dec"]

$("#commentForm").submit(function(e){

    e.preventDefault();

    let dt = new Date();
    let time = dt.getDay() + "" + monthNames[dt.getUTCMonth()] + "," + dt.getFullYear()

    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",
        success: function(response){
            console.log("comment save to db"); 
            
            if(response.bool == true){
                $("#review-res").html("Review Added Scuccesfully..");
               // $(".hide-comment-form").hide();

                let _html = '<div class="d-flex">';
                    _html += '<img src="img/avatar.jpg" class="img-fluid rounded-circle p-3" style="width: 100px; height: 100px;" alt="">';
                    _html += '<div class="">';
                    _html += '<p class="mb-2" style="font-size: 14px;">'+ time +'</p>';
                    _html +=  '<div class="d-flex justify-content-between">';
                    _html +=  '<h5>'+ response.context.user +'</h5>';
                    _html +=  '<div class="d-flex mb-3">';

                    for(let i=0 ; i< response.context.rating ; i++){
                        _html += '<i class="fas fa-star text-warning"></i>';
                    }
                    
                    _html +=   '</div>';
                    _html +=   '</div>';
                    _html +=   '<p>'+ response.context.review +'</p>';
                    _html +=   '</div>';
                    _html +=   '</div>';

                    $(".comment-list").prepend(_html);
            }

        }
    })
})

$(document).ready(function(){
    $(".filter-checkbox, #price-filter-btn").on("click",function(){

        let filter_object = {}
        let min_price = $("#priceRange").attr("min")
        let max_price = $("#priceRange").val()

        filter_object.min_price = min_price;
        filter_object.max_price = max_price;

        $(".filter-checkbox").each(function(){
            let filter_value = $(this).val()
            let filter_key = $(this).data("filter")

           // console.log("filter value is:-",filter_value);
          //  console.log("filter value is:-",filter_key);

            filter_object[filter_key + "[]"] = Array.from(
                document.querySelectorAll('input[data-filter="' + filter_key + '"]:checked')
            ).map(el => el.value)

        })
        console.log("filter object is:",filter_object)
        $.ajax({
            url:'/filter-products/',
            data:filter_object,
            dataType:'json',
            beforeSend:function(){
                console.log("Sending Data.....");
            },
            success:function(response){
                console.log("data filtered succesfully");
                $("#product-wrapper").html(response.data);
                console .log(response);
            }
        });
    });
    $("#amountInput").on("blur", function () {
    let min_price = $("#priceRange").attr("min");
    let max_price = $("#priceRange").attr("max");
    let current_price = $(this).val();

    console.log("Current Price:", current_price);
    console.log("Min Price:", min_price);
    console.log("Max Price:", max_price);

    if(current_price < parseFloat(min_price) || current_price > parseFloat(max_price)){

        min_price = Math.round(min_price * 100)/100;
        max_price = Math.round(max_price * 100)/100;

        console.log("##################################");
        console.log("##################################");
        console.log("##################################");
        console.log("Max price is:-",max_price);
        console.log("Min price is:-",min_price);

        alert("Price must  be between"+ min_price + " and " + max_price);
        $(this).val(max_price);

            // Update slider
        $("#priceRange").val(max_price);

        $(this).focus();
        return false;
    }
});
});

//Add to cart functionality
$(".add-to-cart-btn").on("click",function(){

    let this_val = $(this)
    let index = this_val.attr("data-index")

    let quantity = $(".product-quantity-"+ index).val()
    let product_title = $(".product-title-" + index).val()

    let product_id = $(".product-id-" + index).val()
    let product_price = $(".current-product-price-" + index).val()

    let product_pid = $(".product-pid-" + index).val()
    let product_image = $(".product-image-" + index).val()

    console.log("Quantity",quantity);
    console.log("Title",product_title);
    console.log("Price:",product_price)
    console.log("Id",product_id);
    console.log("PID:",product_id);
    console.log("Image:",product_image);
    console.log("Index:",index);
    console.log("Current Element:",this_val);

     $.ajax({
        url: '/add-to-cart/',
        data:{
            'id':product_id,
            'qty':quantity,
            'title':product_title,
            'price':product_price,
            'image':product_image,
            'pid':product_id,

        },
        dataType:'json',
        beforeSend:function(){
            this_val.html("")
            console.log("Adding product to cart...");
        },
        success: function(response){
            this_val.html("Item added to cart")
            console.log("Added product to cart...");
            $(".cart-items.count").text(response.totalcartitems)
        }
    })
 })


// Use $(document).on to ensure newly added buttons also work
$(document).on("click", ".delete-product", function(e){
    e.preventDefault();

    let product_id = $(this).attr("data-product");
    let this_val = $(this);

    console.log("Product ID:", product_id);
    
    $.ajax({
        // 1. Fixed URL to match your urls.py (delete_from_cart/)
        url: "/delete_from_cart/", 
        data: {
            "id": product_id
        },
        dataType: "json",
        beforeSend: function(){
            this_val.prop("disabled", true);
        },
        success: function(response){
            // 2. Refresh the cart list container
            $("#cart-list").html(response.data);
            
            // 3. Update the counter (ensure key name matches your view)
            $(".cart-items-count").text(response.totalcartitems);
            
            console.log("Item deleted successfully");
        },
        error: function(err) {
            console.log("Error:", err);
            this_val.prop("disabled", false);
        }
    });
});

$(document).on("click", ".update-product", function(e){
    e.preventDefault();

    let product_id = $(this).attr("data-product");
    let this_val = $(this);
    let product_quantity = this_val.closest("tr").find(".product-qty-" + product_id).val();

    // Now we log both to be sure!
    console.log("Product ID:", product_id);
    console.log("Product Quantity:", product_quantity);
    if (!product_quantity || product_quantity < 1) {
        alert("Quantity must be at least 1");
        return;
    }

    $.ajax({
        url:"/update-cart/",
        data:{
            "id":product_id,
            "qty":product_quantity,
        },
        dataType:"json",
        beforeSend:function(){
            this_val.prop("disabled",true)
        },
        success:function(response){
            this_val.show()
            $("#cart-list").html(response.data);
            $(".cart-items-count").text(response.totalcartitems);
        },
        complete: function () {
            this_val.prop("disabled", false);
        }
    })
});

$(document).ready(function () {
    $(document).on("click", "#checkout-btn", function () {
        const url = $(this).attr("data-url");
        console.log("Redirecting to:", url);
        window.location.href = url;
    });
});


$(document).on("click", ".add-to-wishlist", function(e){
    e.preventDefault()

    let product_id = $(this).data("product-item")
    console.log("Wishlist clicked, product:", product_id)

    $.ajax({
    url: "/add-to-wishlist/",
    data: { id: product_id },
    dataType: "json",
    success: function(response){
        console.log("SUCCESS:", response)
    },
    error: function(xhr){
        console.log("ERROR:", xhr.status, xhr.responseText)
    }
})

})


$(document).on("click", ".delete-wishlist-product", function(){
    let wishlist_id = $(this).attr("data-wishlist-product")
    let this_val = $(this) // Store reference to the button clicked

    console.log("Deleting item ID:", wishlist_id);

    $.ajax({
        url: "/delete-from-wishlist/",
        data: {
            "id": wishlist_id
        },
        dataType: "json",
        beforeSend: function(){
            console.log("Deleting product from wishlist....");
        },
        success: function(response){
            $("#wishlist-list").html(response.data)
        }
    })
})