#!/bin/sh

arg="$1"

case $arg in
    "std")
        echo "Switching to valid CSS"
        ln -sf admin_std.css admin.css
        ln -sf cart_std.css cart.css
        ln -sf category_std.css category.css
        ln -sf product_std.css product.css
        ln -sf style_std.css style.css
        ln -sf navi_std.css navi.css
        ln -sf search_std.css search.css
    ;;
    "cool")
        echo "Switching to CSS3"
        ln -sf admin_cool.css admin.css
        ln -sf cart_cool.css cart.css
        ln -sf category_cool.css category.css
        ln -sf product_cool.css product.css
        ln -sf style_cool.css style.css
        ln -sf navi_cool.css navi.css
        ln -sf search_cool.css search.css
    ;;
    *)
        echo "Usage: $0 [std|cool]"
        exit 1
    ;;
esac
