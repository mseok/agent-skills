ObjC.import("Foundation");

const ivantiBundleIdentifier = "net.pulsesecure.Pulse-Secure";

function stringAttribute(element, attributeName) {
  try {
    const value = element.attributes.byName(attributeName).value();
    return value === null ? "" : String(value);
  } catch (_error) {
    return "";
  }
}

function run(argv) {
  const expectedField = argv[0];
  if (expectedField !== "username" && expectedField !== "password") {
    throw new Error("Expected username or password field argument");
  }

  const input = $.NSFileHandle.fileHandleWithStandardInput.readDataToEndOfFile;
  let value = ObjC.unwrap(
    $.NSString.alloc.initWithDataEncoding(input, $.NSUTF8StringEncoding),
  );

  value = value.replace(/\r?\n$/, "");
  if (!value) {
    throw new Error("Keychain value is empty");
  }

  const systemEvents = Application("System Events");
  const frontmostProcesses = systemEvents.applicationProcesses.whose({
    frontmost: true,
  })();
  if (
    frontmostProcesses.length !== 1 ||
    frontmostProcesses[0].bundleIdentifier() !== ivantiBundleIdentifier
  ) {
    value = "";
    throw new Error("Ivanti is not the frontmost application");
  }

  const process = frontmostProcesses[0];
  let focusedElement;
  try {
    focusedElement = process.attributes.byName("AXFocusedUIElement").value();
  } catch (_error) {
    value = "";
    throw new Error("No focused Ivanti accessibility element");
  }

  const role = stringAttribute(focusedElement, "AXRole");
  const subrole = stringAttribute(focusedElement, "AXSubrole");
  if (role !== "AXTextField" && subrole !== "AXSecureTextField") {
    value = "";
    throw new Error("Focused Ivanti element is not a text field");
  }

  const labels = [
    stringAttribute(focusedElement, "AXDescription"),
    stringAttribute(focusedElement, "AXTitle"),
    stringAttribute(focusedElement, "AXPlaceholderValue"),
    stringAttribute(focusedElement, "AXHelp"),
  ]
    .join(" ")
    .toLowerCase();
  const expectedLabels =
    expectedField === "username" ? ["user name", "username"] : ["password"];
  if (!expectedLabels.some((label) => labels.includes(label))) {
    value = "";
    throw new Error(`Focused Ivanti field is not ${expectedField}`);
  }

  try {
    focusedElement.attributes.byName("AXValue").value = value;
  } catch (_error) {
    value = "";
    throw new Error("Unable to set focused Ivanti field");
  }
  value = "";
  return "";
}
