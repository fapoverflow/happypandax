import StateBlock, { defineAtom } from './_base';

export default class _AppState extends StateBlock {
  static theme = defineAtom({
    default: 'light' as 'light' | 'dark',
  });

  static home = defineAtom({ default: '/library' });
  static loggedIn = defineAtom({ default: false });
  static drawerOpen = defineAtom({ default: false });
}