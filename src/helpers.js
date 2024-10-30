import fetch from "isomorphic-unfetch";
import { nanoid } from "nanoid";

//fetcher
export const fetcher = (url) => fetch(url).then((r) => r.json());

export const getFormValidations = () => {
  return {
    //name
    name: {
      required: {
        value: true,
        message: "Nama wajib diisi",
      },
      maxLength: {
        value: 50,
        message: "Maksimal 50 karakter",
      },
      minLength: {
        value: 3,
        message: "Minimal 3 karakter",
      }
    },

    //phone
    phone: {
      required: {
        value: true,
        message: "No WA wajib diisi",
      },
      maxLength: {
        value: 20,
        message: "Maksimal 20 karakter",
      },
      minLength: {
        value: 5,
        message: "Minimal 5 karakter",
      },
      pattern: {
        value: /^[0-9]{5,20}$/,
        message: "No WA tidak valid",
      },
    },
    //address
    address: {
      required: {
        value: true,
        message: "Alamat & Kode Pos wajib diisi",
      },
      maxLength: {
        value: 150,
        message: "Maksimal 150 karakter",
      },
      minLength: {
        value: 5,
        message: "Minimal 5 karakter",
      },
    },
    //extra comment
    comment: {
      maxLength: {
        value: 100,
        message: "Maksimal 100 karakter",
      },
    },
  };
};

//wsp url creator
export function getWspUrl(orderData) {
  const N = process.env.NEXT_PUBLIC_MY_PHONE_NUMBER;
  const ID = nanoid(8);
  const { cartItems, subTotal, withDelivery, formData } = orderData;
  const { name, phone, address, comment } = formData;

  let cartListforUrl = "";

  {
    Object.values(cartItems).forEach((item) => {
      const itemTotal = (item.offerPrice ? item.offerPrice * item.qty : item.price * item.qty).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
      cartListforUrl += `%0A%0A - *(${item.qty})* ${item.title} --> _*Rp. ${itemTotal}*_`;
    });
  }

  const WSP_URL = `https://api.whatsapp.com/send/?phone=${N}&text=%2A${"Order"}%3A%2A%20${ID}%0A%0A%2A${"Client"}%3A%2A%20${name}%0A%0A%2A${"Phone"}%3A%2A%20${phone}%0A%0A%2A${
    withDelivery ? "Address" + "%3A%2A%20" + address + " %0A%0A%2A" : ""
  }${
    comment ? "Comment" + "%3A%2A%20" + comment + "%0A%0A%2A" : ""}
    %3A%2A${"Items List"}%3A%2A${cartListforUrl}%0A%0A%2A${
    withDelivery ? "Sub Total" + "%3A%2A%20Rp. " + subTotal + " %0A%0A%2A" : ""
  }`;

  return WSP_URL;
}
