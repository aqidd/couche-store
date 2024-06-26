import { Flex, Text } from "@chakra-ui/core";

export default function OrderItem({ item }) {
  const { qty, title, price, offerPrice } = item;

  const itemTotal = (offerPrice ? offerPrice * qty : price * qty).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");

  return (
    <Flex w="100%" justify="space-between" mt="4">
      <span>
        <b>{qty}</b>
      </span>
      <span>x</span>
      <Text w="70%">{title}</Text>

      <Text>Rp. {itemTotal}</Text>
    </Flex>
  );
}
