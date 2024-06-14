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
