'use client';

import { useContext } from 'react';
import { CartContext } from '@/context/CartContext';

export function useCart() {
  const { state, dispatch } = useContext(CartContext);

  const totalItems = state.items.reduce((sum, item) => sum + item.quantity, 0);

  return {
    items: state.items,
    isOpen: state.isOpen,
    totalItems,
    addItem: (productId: string, size: string, color: string) =>
      dispatch({ type: 'ADD_ITEM', payload: { productId, size: size as import('@/types').Size, color: color as import('@/types').EarthColor } }),
    removeItem: (productId: string, size: string, color: string) =>
      dispatch({ type: 'REMOVE_ITEM', payload: { productId, size, color } }),
    updateQuantity: (productId: string, size: string, color: string, quantity: number) =>
      dispatch({ type: 'UPDATE_QUANTITY', payload: { productId, size, color, quantity } }),
    toggleCart: () => dispatch({ type: 'TOGGLE_CART' }),
    closeCart: () => dispatch({ type: 'CLOSE_CART' }),
    clearCart: () => dispatch({ type: 'CLEAR_CART' }),
  };
}
