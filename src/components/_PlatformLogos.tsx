// Central platform logo map for all categories
import zomatoLogo from '../logos/zomato.png';
import swiggyLogo from '../logos/swiggyinstamart.png';
import blinkitLogo from '../logos/blinkit.png';
import zeptoLogo from '../logos/zepto.png';
import dunzoLogo from '../logos/dunzo.png';
import jiomartLogo from '../logos/jiomart.png';
import moreLogo from '../logos/more.png';
import bigbasketLogo from '../logos/bigbasket.png';
import olaLogo from '../logos/Ola.png';
import uberLogo from '../logos/uber.png';
import nammaYathriLogo from '../logos/namaya3.png';
import rapidoLogo from '../logos/rapido.png';
import amazonLogo from '../logos/amazon.png';
import flipkartLogo from '../logos/flipkart.png';
import myntraLogo from '../logos/myntra.png';
import meeshoLogo from '../logos/meesho.png';
import ajioLogo from '../logos/ajio.png';

export const platformLogoMap: { [key: string]: string } = {
  zomato: zomatoLogo,
  swiggy: swiggyLogo,
  blinkit: blinkitLogo,
  zepto: zeptoLogo,
  dunzo: dunzoLogo,
  jiomart: jiomartLogo,
  more: moreLogo,
  bigbasket: bigbasketLogo,
  ola: olaLogo,
  uber: uberLogo,
  nammayanthri: nammaYathriLogo,
  rapido: rapidoLogo,
  amazon: amazonLogo,
  flipkart: flipkartLogo,
  myntra: myntraLogo,
  meesho: meeshoLogo,
  ajio: ajioLogo,
};

export function getPlatformLogo(key: string): string | undefined {
  let logoKey = key?.toLowerCase().replace(/\s/g, '');
  if (!logoKey) return undefined;
  if (logoKey.includes('instamart')) logoKey = 'swiggy';
  if (logoKey.includes('nammayathri') || logoKey.includes('nammayanthri')) logoKey = 'nammayanthri';
  return platformLogoMap[logoKey];
}
