import { useEffect, useState } from "react";
import { Linking, StyleSheet, Text, TextInput } from "react-native";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import {
  Body,
  Card,
  ErrorState,
  Heading,
  Loading,
  PrimaryButton,
} from "@/src/components/UI";
import { checkout, getCatalog, type CatalogItem } from "@/src/api/care";
import { colors } from "@/src/config/theme";
export default function BillingScreen() {
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [billingPhone, setBillingPhone] = useState("");
  useEffect(() => {
    getCatalog()
      .then(({ services, packages }) => setItems([...services, ...packages]))
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load the catalog."))
      .finally(() => setBusy(false));
  }, []);
  const buy = async (item: CatalogItem) => {
    if (!/^\+?20[0-9]{10}$/.test(billingPhone)) {
      setError("Enter a valid Egyptian mobile number in +20 format.");
      return;
    }
    try {
      setBusy(true);
      const data = await checkout(
        item.service_id
          ? { service_id: item.service_id, billing_phone: billingPhone }
          : { package_id: item.package_id, billing_phone: billingPhone },
      );
      if (data.payment_url) await Linking.openURL(data.payment_url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not start payment.");
    } finally {
      setBusy(false);
    }
  };
  return (
    <AppShell active="more">
      <BrandHeader
        title="Sessions & packages"
        subtitle="Secure payment in Egyptian pounds. No automatic renewal."
      />
      {busy && !items.length ? <Loading /> : null}
      {error ? <ErrorState message={error} /> : null}
      <Text style={styles.label}>Billing mobile number</Text>
      <TextInput
        accessibilityLabel="Billing mobile number"
        autoComplete="tel"
        keyboardType="phone-pad"
        placeholder="+201001234567"
        value={billingPhone}
        onChangeText={(value) => setBillingPhone(value.trim())}
        style={styles.input}
      />
      {items.map((item) => (
        <Card key={item.service_id || item.package_id}>
          <Heading>{item.name_en}</Heading>
          {item.sessions_count ? (
            <Body muted>{item.sessions_count} sessions</Body>
          ) : null}
          <Heading>
            {(item.price_minor / 100).toLocaleString("en-EG")} EGP
          </Heading>
          <PrimaryButton
            title="Continue to Paymob"
            disabled={busy}
            onPress={() => buy(item)}
          />
        </Card>
      ))}
    </AppShell>
  );
}

const styles = StyleSheet.create({
  label: { color: colors.text, fontSize: 14, fontWeight: "700" },
  input: { minHeight: 48, borderWidth: 1, borderColor: colors.border, borderRadius: 14, paddingHorizontal: 14, backgroundColor: colors.card, color: colors.text },
});
