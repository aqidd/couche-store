import { ThemeProvider, CSSReset } from "@chakra-ui/core";
import Head from "next/head";
import { RecoilRoot } from "recoil";
import theme from "../theme";

function MyApp({ Component, pageProps }) {
  return (
    <>
      <Head>
        <link rel="stylesheet" href="/styles.css" />
        <link rel="icon" href="/images/favicon.ico" />
        <meta name="description" content="cari sprei lokal, jepang, tencel dan katun egypt dengan kualitas terbaik." />
        <meta name="keywords" content="sprei, lokal, jepang, tencel, katun Mesir, beli sprei, sprei kasur" />
        <title>Couche Home - Toko Sprei Berkualitas Terbaik</title>
        <meta name="robots" content="index, follow" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta property="og:title" content="Toko Sprei Berkualitas Terbaik" />
        <meta property="og:description" content="cari sprei lokal, jepang, tencel dan katun egypt dengan kualitas terbaik." />
        <meta property="og:image" content="/images/banner.jpeg" />
        <meta property="og:url" content="https://couchehome.com" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Couche Home - Toko Sprei Berkualitas Terbaik" />
        <meta name="twitter:description" content="cari sprei lokal, jepang, tencel dan katun egypt dengan kualitas terbaik." />
        <meta name="twitter:image" content="/images/banner.jpeg" />
      </Head>

      <RecoilRoot>
        <ThemeProvider theme={theme}>
          <CSSReset />
          <Component {...pageProps} />
        </ThemeProvider>
      </RecoilRoot>
    </>
  );
}

export default MyApp;
