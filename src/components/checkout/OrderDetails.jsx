import { Box, Divider, Flex, Heading, Text } from "@chakra-ui/core";
import OrderItem from "./OrderItem";
import { useRecoilValue } from "recoil";
import { orderDetails } from "../../recoil/state";

function OrderDetails() {
  const { cartItems, subTotal, withDelivery, shippingCost, total } = useRecoilValue(orderDetails);

  return (
    <Box w={["100%", "90%", "46%", "35%"]} height="max-content" p="4" mx="2">
      <Heading as="h3" size="md" textAlign="center">
        Pesanan Anda
      </Heading>

      <Flex direction="column" align="center" p="2" mt="4" overflowY="auto" w="100%" maxHeight="400px">
        {Object.values(cartItems).map((item) => (
          <OrderItem key={item.id} item={item} />
        ))}
      </Flex>

      <Divider my="2" />

      <Flex direction="column" p="2" w="100%">
        <Flex w="100%" justify="space-between" mb="3">
          <Text>Sub Total</Text>
          <Text>Rp. {subTotal.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")}</Text>
        </Flex>

        {/* TODO uncomment this for delivery */}
        {/* <Flex w="100%" justify="space-between" mb="3">
          <Text>Delivery</Text>
          <Text>Rp. {withDelivery ? shippingCost : "0"}</Text>
        </Flex> */}

        <Flex w="100%" justify="space-between" mb="3">
          <Text fontSize="lg" fontWeight="medium">
            Total
          </Text>
          <Text fontSize="lg" fontWeight="medium">
            Rp. {total.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")}
          </Text>  
        </Flex>

        <Flex w="100%" justify="space-between" mb="3">
          <div>
            <iframe src={`http://rajaongkir.com/widget/frame?t=light&h=${typeof window !== 'undefined' ? window.location.host : ''}`} height="385px" style={{border:'0px'}} border="0" frameBorder="0"></iframe>
          </div>
        </Flex>
      </Flex>
    </Box>
  );
}

export default OrderDetails;
