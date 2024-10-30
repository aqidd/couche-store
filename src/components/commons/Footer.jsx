import { Box, Flex, Icon, Stack, Text } from "@chakra-ui/core";

function Footer() {
  return (
    <Box as="footer" w="100%" bg="bluex.500" color="white" position="relative" zIndex="1101">
      <Flex w="90%" mx="auto" justify="space-between" align="center" py="6">
        <Text>2024 - Couche Home</Text>

        <Stack isInline>
          <a href="#">
            <Icon name="instagram" mx="2" />
          </a>
          <a href="#">
            <Icon name="facebook" mx="2" />
          </a>
          <a href="#">
            <Icon name="whatsapp" mx="2" />
          </a>
        </Stack>
      </Flex>
    </Box>
  );
}

export default Footer;
